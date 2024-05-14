from sql_translator import SqlTranslator


class TestSqlTranslator:
  def __init__(self):
     pass
  
  def run_test_suite(self, oai_type):
     self.test_translate_from_redshift_to_snowflake_01(oai_type)
     self.test_translate_from_redshift_to_snowflake_02(oai_type)
    #  self.test_translate_from_redshift_to_snowflake_03(oai_type)
     self.test_translate_from_redshift_to_snowflake_04(oai_type)

    
  def test_translate_from_redshift_to_snowflake_01(self, oai_type):
    sql_translator = SqlTranslator("Redshift", "Snowflake", oai_type)
    sql_stmt_needs_hint = """
      "select  \"column\" from pg_table_def where UPPER(tablename) = UPPER('" + context.input_staging_table_name + "') and UPPER(schemaname) = UPPER('" + context.DMConnectionReadWrite_SchemaStrategic + "')" 
    """
    translated_sql_example = sql_translator.translate_sql(sql_stmt_needs_hint)
    print(translated_sql_example)

  def test_translate_from_redshift_to_snowflake_02(self, oai_type):
    sql_translator = SqlTranslator("Redshift", "Snowflake", oai_type)
    sql_stmt = """
      SELECT DATE_TRUNC('day', order_date) FROM public.orders;

      SELECT username, 
            COUNT(order_id) AS total_orders
      FROM public.users u
      JOIN public.orders o ON u.user_id = o.user_id
      WHERE DATE_TRUNC('month', o.order_date) = '2022-01-01'
      GROUP BY username
      ORDER BY total_orders DESC
      LIMIT 10;
    """
    translated_sql_example = sql_translator.translate_sql(sql_stmt)
    print(translated_sql_example)

  def test_translate_from_redshift_to_snowflake_03(self, oai_type):
    sql_translator = SqlTranslator("Redshift", "Snowflake", oai_type)
    sql_stmt = """
      SELECT 
          username,
          position('a' in email) as position_in_email,
          getdate() as current_date,
          date_part('year', birth_date) as birth_year,
          sysdate as system_date,
          convert(VARCHAR, order_date, 112) as order_date_string,
          COALESCE(job_title, 'N/A') as job
      FROM 
          public.users
      WHERE 
          date_part('month', birth_date) = 7;
          
      CASE 
          WHEN COALESCE(from_source.TECHNO_HLX, 0) = 0 THEN 'commandes services HLX autre que acces'
          WHEN from_source.DupRec > 1 AND from_source.TECHNO_HLX = 1 THEN 'incoherence(s) CEIA - doublons'
          WHEN from_source.NUM_CLIENT_SGA IS NULL AND from_source.EXT_CUST_ID_ETIYA IS NOT NULL AND 
              UPPER(from_source.NOM_CLI) = UPPER(REPLACE(COALESCE(from_source.LST_NAME, ''), '\u0398', 'e')) AND 
              UPPER(from_source.PREN_CLI) = UPPER(REPLACE(COALESCE(from_source.FRST_NAME, ''), '\u0398', 'e')) 
          THEN 'incoherence(s) MDM EDV - meme nom et prenom SGA et Etiya'
          WHEN from_source.TV_SGA = 1 OR from_source.INT_SGA = 1 OR from_source.CLUB_ILLICO_SGA = 1 OR 
              from_source.GR_699 = 1 OR from_source.NOTE_20189 = 1 OR from_source.EXT_CUST_ID_ETIYA = 1 OR 
              from_source.COURRIEL_SGA = 1 
          THEN 'avec incoherence(s)'
          WHEN from_source.EXT_CUST_ID_ETIYA = 3 THEN 'incoherence(s) MDM EDV et EXT_CUST_ID_ETIYA'
          WHEN from_source.EXT_CUST_ID_ETIYA = 2 THEN 'incoherence(s) nom et prenom SGA et Etiya - non match EDV'
          ELSE 'sans incoherence(s)'
      END
    """
    translated_sql_example = sql_translator.translate_sql(sql_stmt)
    print(translated_sql_example)

  def test_translate_from_redshift_to_snowflake_04(self, oai_type):
    sql_translator = SqlTranslator("Redshift", "Snowflake", oai_type)
    sql_stmt = """
    ((String) globalMap.get("templateInsertNewRowsSql"))
    """
    translated_sql_example = sql_translator.translate_sql(sql_stmt)
    print(translated_sql_example)

if __name__ == '__main__':
    test_sql_translator = TestSqlTranslator()
    test_sql_translator.run_test_suite("openai")

