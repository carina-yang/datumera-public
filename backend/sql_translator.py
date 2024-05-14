import argparse
import requests
import asyncio
from ratelimiter import RateLimiter
import os
from config.ai_bot_config import *
from libs.prompt_generator import PromptGenerator
from libs.ai_api_utils import AiApiUtils
import json

# oai_api_type_default = os.environ.get("OAI_API_TYPE", 'azure')
oai_api_type_default = "openai"
oai_model_default = os.environ.get("OAI_MODEL", "gpt-4")
retry_limit_default = int(os.environ.get("RETRY_LIMIT_DEFAULT", "1"))
retry_interval = int(os.environ.get("RETRY_INTERVAL", "15"))
err_msgs = ["--to be reviewed", "--Statement is too big to auto-split for translation."]

class SqlTranslator:
     
    def __init__(self, src_lan, tgt_lan, sql_identifier_pattern, sql_match_pattern, oai_api_type="openai", oai_model="gpt-4"):
        self.src_lan = src_lan
        self.tgt_lan = tgt_lan
        self.sql_identifier_pattern = sql_identifier_pattern
        self.sql_match_pattern = sql_match_pattern
        self.ai_bot = AiBot(oai_api_type, oai_model)
        self.prompt_generator = PromptGenerator(self.src_lan, self.tgt_lan)
        self.request_limiter = RateLimiter(max_calls=self.ai_bot.ai_config["requests_per_minute_limit"], period=60)
        self.token_limiter = RateLimiter(max_calls=self.ai_bot.ai_config["tokens_per_minute_limit"], period=60)
        self.token_limit = int(self.ai_bot.ai_config["max_tokens"]*0.90/2)
        self.token_limit_upper = -1
        if oai_api_type.lower()=="azure" and oai_model=="gpt-4":
            self.token_limit_upper = int(self.ai_bot.ai_bot_configs["azure"]["gpt-4-32k"]["max_tokens"]*0.90/2)

    def translate_sql_api(self, in_src):
        prompt_msgs = self.prompt_generator.generate_prompt_msgs(in_src)
        return self.call_openai_api(prompt_msgs)
        

    def translate_sql(self, in_src):
        prompt_msgs = self.prompt_generator.generate_prompt_msgs(in_src)
        return self.call_openai_pi_chat_completion(self.ai_bot.get_openai(), prompt_msgs)

    async def call_openai_pi(self, openai_pi, prompt_msgs, max_tokens_len=ai_bot_params_default["max_tokens"], temperature=ai_bot_params_default["temperature"]):
        return self.call_openai_pi_chat_completion(openai_pi, prompt_msgs, max_tokens_len, temperature)
    
    def call_openai_pi_chat_completion(self, openai_pi, prompt_msgs, max_tokens_len=ai_bot_params_default["max_tokens"], temperature=ai_bot_params_default["temperature"]):
        max_token_num_in_repsonse = max_tokens_len - AiApiUtils.num_tokens_from_messages(prompt_msgs, self.ai_bot.ai_config["model"])
        response = openai_pi.ChatCompletion.create(
          model=self.ai_bot.ai_config["model"], 
          engine=(None if self.ai_bot.ai_config["api_type"]=='openai' else self.ai_bot.ai_config["engine"]),
          max_tokens = max_token_num_in_repsonse,
          temperature=temperature,
          messages=prompt_msgs
        )
        result = response.choices[0]["message"]["content"]
        return result


    def call_openai_api(self, prompt_msgs, response_length=ai_bot_params_default["max_tokens"], temperature=ai_bot_params_default["temperature"]):
        headers = {
            "Content-Type": "application/json"
        }
        if self.ai_bot.ai_config["authentication"]=="api-key":
            headers["api-key"] = self.ai_bot.ai_config['api_key']
        else:
            headers["Authorization"] = f"Bearer {self.ai_bot.ai_config['api_key']}"

        data = {
            "messages": prompt_msgs,
            "max_tokens": response_length,
            "temperature": temperature
        }
        if self.ai_bot.oai_api_type.lower() == "openai":
            data["model"] = self.ai_bot.ai_config['engine']
        elif self.ai_bot.oai_api_type.lower() == "azure":
            data["engine"] = self.ai_bot.ai_config['engine']

        oai_endpoint = self.ai_bot.get_api_endpoint()

        response = requests.post(oai_endpoint, headers=headers, json=data)
        response_data = response.json()

        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            raise ValueError("Failed to get a response from OpenAI API")
        

    async def translate_sql_file(self, content, filename):
        system_msg = self.prompt_generator.generate_system_prompt_msg_with_sql_id_pattern(self.sql_identifier_pattern)
        system_msg_tokens = AiApiUtils.num_tokens_from_messages([system_msg])
        all_hints = list()
        all_added_stmts = ""
        empty_user_msg_content = self.prompt_generator.get_user_message_content_template().format(sql="", user_hints="")
        user_msg_content = empty_user_msg_content
        user_msg_tokens = AiApiUtils.num_tokens_from_messages([self.prompt_generator.get_user_message(user_msg_content)])
        sql_stmts = AiApiUtils.split_sql_statements_by_identifier_str(content, self.sql_match_pattern)
        for sql_id, sql_stmt in sql_stmts.items():
            if sql_stmt.strip():
                sql_stmt = sql_stmt.strip()
                hint_list = self.prompt_generator.get_hints(sql_stmt)
                hints_diff = [h for h in hint_list if h not in all_hints]
                added_hint_msg = ""
                added_hint_tokens = 0
                if hints_diff:
                    added_hint_msg = "\n".join(hints_diff) + "\n"
                    added_hint_tokens = AiApiUtils.num_tokens_from_message(added_hint_msg)
                added_sql = f"\n--~BL_{sql_id}_BL~\n{sql_stmt}\n"
                added_sql_tokens = AiApiUtils.num_tokens_from_message(added_sql)
                expected_total_tokens = system_msg_tokens + user_msg_tokens + added_hint_tokens + added_sql_tokens
                if expected_total_tokens > self.token_limit:
                    if user_msg_content == empty_user_msg_content:
                        if self.token_limit_upper!=-1 and expected_total_tokens < self.token_limit_upper:
                            user_msg_content = self.prompt_generator.get_user_message_content_template().format(sql=added_sql, user_hints=added_hint_msg)
                            await self.process_user_message(self.ai_bot.get_openai_by_type_and_model("azure", "gpt-4-32k"), system_msg, user_msg_content, added_sql, self.ai_bot.ai_bot_configs["azure"]["gpt-4-32k"]["max_tokens"], filename)
                        else: ##cannot handled by both gpt-4 and gpt-4-32k
                            logging.error(f"SQL file {filename} contains statement which is too big to auto-split.")
                            self.save_response(filename, added_sql + "--Statement is too big to auto-split for translation.", added_sql)
                        all_hints.clear()
                        all_added_stmts = ""
                        user_msg_content = empty_user_msg_content
                        user_msg_tokens = AiApiUtils.num_tokens_from_messages([self.prompt_generator.get_user_message(user_msg_content)])
                        continue
                    else:
                        await self.process_user_message(self.ai_bot.get_openai(), system_msg, user_msg_content, all_added_stmts, self.ai_bot.ai_config["max_tokens"], filename)
                        all_hints.clear()
                        all_added_stmts = ""
                        user_msg_content = empty_user_msg_content
                        user_msg_tokens = AiApiUtils.num_tokens_from_messages([self.prompt_generator.get_user_message(user_msg_content)])
                        hints_diff = [h for h in hint_list if h not in all_hints]
                        added_hint_msg = ""
                        added_hint_tokens = 0
                        if hints_diff:
                            added_hint_msg = "\n".join(hints_diff) + "\n"
                            added_hint_tokens = AiApiUtils.num_tokens_from_message(added_hint_msg)

                all_added_stmts = all_added_stmts + added_sql
                for h in hints_diff:
                    if h not in all_hints:
                        all_hints.append(h)
                user_msg_content = self.prompt_generator.get_user_message_content_template().format(sql=all_added_stmts, user_hints=("\n".join(all_hints) + "\n"))
                user_msg_tokens += (added_hint_tokens + added_sql_tokens)
        
        if user_msg_content and user_msg_content != empty_user_msg_content: 
            await self.process_user_message(self.ai_bot.get_openai(), system_msg, user_msg_content, all_added_stmts, self.ai_bot.ai_config["max_tokens"], filename)


    async def process_user_message(self, openai_pi, system_msg, user_msg_content, src_sqls, max_tokens_len, filename):
        retries = 0
        success = False
        messages = [system_msg, self.prompt_generator.get_user_message(user_msg_content)]
        while retries < retry_limit_default:
            try:
                with self.request_limiter:
                    with self.token_limiter:
                        response_content = await self.call_openai_pi(openai_pi, messages, max_tokens_len=max_tokens_len)
                        self.save_response(filename, response_content, src_sqls)
                        success = True
                        break
            except Exception as e:
                logging.error(e)
                retries += 1
                await asyncio.sleep(retry_interval)
        
        if not success:
            err = f"--Failed translation after retrying {retry_limit_default} times"
            src_sql_stmts = AiApiUtils.split_sql_statements_by_identifier_str(src_sqls, self.sql_match_pattern)
            with open(AiApiUtils.get_translated_file_path(filename), 'a') as t_file, open(AiApiUtils.get_translated_errors_path(filename), 'a') as r_file:
                for sql_id, sql_stmt in src_sql_stmts.items():
                    e = {
                        "id": sql_id,
                        "source": sql_stmt,
                        "target": "",
                        "error": err
                    }
                    j_str = json.dumps(e)
                    r_file.write(j_str + "\n")
                    t_file.write(f"\n--~BL_{sql_id}_BL~\n{sql_stmt}\n")


    @staticmethod
    def extract_content_from_quote(text):
        lines = text.strip().split('\n')
        start = 0
        if lines[0].strip() == '"':
            start = 1
        end = len(lines)
        if lines[-1].strip() == '"':
            end = -1
        return '\n'.join(lines[start:end])

    def save_response(self, filename, response_content, src_sqls):
            result = self.extract_content_from_quote(response_content)
            sql_stmts = AiApiUtils.split_sql_statements_by_identifier_str(result, self.sql_match_pattern)
            src_sql_stmts = AiApiUtils.split_sql_statements_by_identifier_str(src_sqls, self.sql_match_pattern)
            with open(AiApiUtils.get_translated_file_path(filename), 'a') as t_file, open(AiApiUtils.get_translated_errors_path(filename), 'a') as r_file:
                for sql_id, src_sql_stmt in src_sql_stmts.items():
                    sql_stmt = sql_stmts.get(sql_id)
                    if sql_stmt is None:
                        e={
                            "id": sql_id,
                            "source": src_sql_stmt,
                            "target": "",
                            "error": "--missed translation."
                        }
                        j_str = json.dumps(e)
                        r_file.write(j_str + "\n")
                        t_file.write(f"\n--~BL_{sql_id}_BL~\n{src_sql_stmt}\n")
                        continue
                    t_res = sql_stmt
                    for err in err_msgs:
                        if err in sql_stmt:
                            t_res = t_res.replace(err, "")
                            e = {
                                "id": sql_id,
                                "source": src_sql_stmts.get(sql_id),
                                "target": t_res,
                                "error": err
                            }
                            j_str = json.dumps(e)
                            r_file.write(j_str + "\n")
                    t_file.write(f"\n--~BL_{sql_id}_BL~\n{t_res}\n")


    def translate_sql_file_validation(self, content, filename):
        system_msg = self.prompt_generator.generate_system_prompt_msg()
        total_tokens = AiApiUtils.num_tokens_from_messages(system_msg["content"])
        sql_stmts = AiApiUtils.split_sql_statements(content)
        if len(sql_stmts)==1:
            if len(sql_stmts[0])==0:
                logging.warn(f"The source SQL file {filename} is empty.")
                self.save_response(filename, content)
                return False
            else:
                hint = self.prompt_generator.generate_user_prompt_msg(sql_stmts[0])
                total_tokens_tmp = total_tokens + AiApiUtils.num_tokens_from_messages(hint)
                if total_tokens_tmp > self.token_limit:
                    if self.token_limit_upper!=-1 and total_tokens_tmp < self.token_limit_upper:
                        raise ValueError("SQL file fit gpt4-32k")
                    else:
                        logging.error(f"SQL file {filename} too big to auto-split.")
                        self.save_response(filename, content + "--Statement is too big to auto-split for translation.")
                        return False
        return True
    

def split_sql_files_to_translate(in_dir, src_lan, tgt_lan, sql_identifier_pattern, sql_match_pattern, oai_api_type=oai_api_type_default, oai_model=oai_model_default):
    sql_translator = SqlTranslator(src_lan, tgt_lan, sql_identifier_pattern, sql_match_pattern, oai_api_type, oai_model)
    # loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = []

    for filename in os.listdir(in_dir):
        if filename.endswith('.sql'):
            with open(os.path.join(in_dir, filename), 'r') as sql_file:
                content = sql_file.read()
                tasks.append(sql_translator.translate_sql_file(content, os.path.join(in_dir, filename)))
    
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()


def create_arg_parse():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="cmd")
    
    translate_parser = subparsers.add_parser("translate", description="Translate SQL files")
    translate_parser.add_argument("source_db", help="source db type")
    translate_parser.add_argument("target_db", help="target db type")
    translate_parser.add_argument("--sql_identifier_pattern", default=";", help="A pattern to identify individual SQL statement.")
    translate_parser.add_argument("--sql_match_pattern", default=";", help="A pattern to match and extract SQL statements.")
    translate_parser.add_argument("--src_dir", help="directory where SQL source files are")
    translate_parser.add_argument("--oai_api_type", default=oai_api_type_default, help="AI API type, default is azure. The acceptable value is openai or azure")
    translate_parser.add_argument("--oai_model", default=oai_model_default, help="AI model type, default is gpt-4. The acceptable value is gpt-4 or gpt-4-32k.")
    return parser

def main():
    parser = create_arg_parse()
    args = parser.parse_args()

    if args.cmd == "translate":
        split_sql_files_to_translate(args.src_dir, args.source_db, args.target_db, args.sql_identifier_pattern, args.sql_match_pattern, args.oai_api_type, args.oai_model)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
    main()