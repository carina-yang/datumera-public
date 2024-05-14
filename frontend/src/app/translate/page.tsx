'use client'
import MaxWidthWrapper from "@/components/MaxWidthWrapper";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { BuyCreditsDialog } from "@/components/BuyCreditsDialog";
import { useUserData } from "@/lib/hooks";
import { useAuth } from "@/context/AuthContextProvider";
import { redirect } from "next/navigation";
import { useState } from "react";
import { zipFile, prependLineToFileBlob, removeIdentifierPattern } from "@/lib/utils";
import JSZip from 'jszip';

const Translate = () => {
    const { user } = useAuth();
    if (!user || !user.uid) redirect('/')
    const data = useUserData(`users/${user.uid}`);

    const [srcLang, setSrcLang] = useState('');
    const [tgtLang, setTgtLang] = useState('');
    const [sqlFile, setSqlFile] = useState<File | null>(null);
    const [translatedSQL, setTranslatedSQL] = useState('');

    const handleSrcLangChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSrcLang(e.target.value)
        console.log(e.target.value);
    };
    const handleTgtLangChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setTgtLang(e.target.value)
        console.log(e.target.value);
    };
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSqlFile(e.target.files[0]);
        }
    };

    const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
        e.preventDefault();
        if (!sqlFile || !srcLang || !tgtLang) {
            alert("Please fill in all fields and select a file.");
            return;
        }
    
        try {
            const lineToPrepend = '--~BL_023_000_BL~';
            const modifiedBlob = await prependLineToFileBlob(sqlFile, lineToPrepend);
    
            const zippedFile = await zipFile(modifiedBlob, sqlFile.name) as Blob;
    
            const formData = new FormData();
            formData.append('sql_package_file', zippedFile, `${Date.now()}_package.zip`);
            formData.append('src_lan', srcLang);
            formData.append('tgt_lan', tgtLang);
            formData.append('sql_identifier_pattern', "--~BL_\\d{3}_\\d{3}_BL~\\n");
            formData.append('sql_match_pattern', "(--~BL_(\\d{3})_(\\d{3})_BL~\\n)(.*?)(?=--~BL_\\d{3}_\\d{3}_BL~\\n|$)");
    
            const idToken = await user.getIdToken();
    
            const response = await fetch('http://localhost:8000/translate_sql', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${idToken}`,
                },
                body: formData,
            });
    
            if (response.ok) {
                const blob = await response.blob();
                const zip = new JSZip();
                const contents = await zip.loadAsync(blob);
    
                const sqlFileEntry = Object.values(contents.files).find(file => file.name.endsWith('.sql'));

                if (sqlFileEntry) {
                    const fileContents = await sqlFileEntry.async('string');
                    // Update the state linked to the second textarea
                    const justSQL = removeIdentifierPattern(fileContents, lineToPrepend);
                    console.log(justSQL);
                    setTranslatedSQL(justSQL);
                } else {
                    alert('No SQL file found in the zip.');
                }
            } else {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    const sqlLanguages = [
        { value: 'MySQL', label: 'MySQL' },
        { value: 'Postgres', label: 'Postgres'},
        { value: 'Redshift', label: 'Redshift'},
        { value: 'Snowflake', label: 'Snowflake'}
      ];

  return (
    <>
        <MaxWidthWrapper>
        <div className="flex flex-col items-start justify-between sm:flex-row sm:items-center sm:space-y-0 md:h-16">
            <h2 className="text-lg font-semibold">Translate</h2>
         </div>
         <div className="flex flex-col gap-6">
            <div className="grid sm:grid-cols-2 gap-6">
                <div className="grid gap-1">
                    <Label className="block text-sm font-medium leading-6 text-gray-900">
                    Translate from:
                    </Label>
                    <select 
                        id="select-from" 
                        className="border border-gray-400 rounded-md p-2 text-sm font-medium"
                        value={srcLang}
                        onChange={handleSrcLangChange}
                    >
                        {sqlLanguages.map((sqlLanguage) => (
                            <option value={sqlLanguage.value}>
                            {sqlLanguage.label}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="grid gap-1">
                    <Label className="block text-sm font-medium leading-6 text-gray-900">
                        Translate to:
                    </Label>
                    <select 
                        id="select-to" 
                        className="border border-gray-400 rounded-md p-2 text-sm font-medium"
                        value={tgtLang}
                        onChange={handleTgtLangChange}
                    >
                        {sqlLanguages.map((sqlLanguage) => (
                            <option value={sqlLanguage.value}>
                            {sqlLanguage.label}
                            </option>
                        ))}
                    </select>
                </div>
            </div>
            <div className="grid lg:grid-cols-2 gap-6">
                <div className="grid gap-1">
                    <Label htmlFor="sql-file" className="block text-sm font-medium leading-6 text-gray-900" >Or, upload your SQL file here:</Label>
                    <Input 
                        id="sql-file" 
                        type="file"
                        onChange={handleFileChange} />
                </div>
            </div>
            <div className="grid sm:grid-rows-2 lg:grid-cols-2 gap-6 h-[450px]">
                <div>
                    <Textarea placeholder="Enter your SQL here" className=" h-96 mb-5 resize-none"/>
                    <Button onClick={handleSubmit}>Translate</Button>
                </div>
                <Textarea value={translatedSQL} placeholder="Your translated SQL will be here" className=" h-96 resize-none"/>
            </div>
            <div className=" mb-4 flex gap-5 items-center">
                <p>You have <strong>{data?.credits} credits</strong> remaining</p>
                <BuyCreditsDialog />
            </div>
         </div>
        </MaxWidthWrapper>
    </>
  );
};

export default Translate;
