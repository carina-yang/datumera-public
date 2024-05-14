import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import JSZip from 'jszip';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function zipFile(file: Blob, fileName: string) {
  const zip = new JSZip();
  // Assuming `file` is the File object you want to zip.
  // The "file.name" is used as the name inside the zip file.
  // You can customize this string to change the file's name inside the zip.
  zip.file(fileName, file);

  try {
    // Generate the zip file as a Blob
    const content = await zip.generateAsync({ type: "blob" });

    // Returns a Blob ready to be sent with a FormData
    return content;
  } catch (error) {
    console.error("Error zipping the file: ", error);
  }
};

// Helper function to prepend a line to the file content and return a new Blob
export async function prependLineToFileBlob(fileBlob: Blob, lineToPrepend: string): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result || '';
      if (typeof text === 'string') {
        const modifiedText = lineToPrepend + '\n' + text;
        const modifiedBlob = new Blob([modifiedText], { type: 'text/plain' });
        resolve(modifiedBlob);
      } else {
        reject(new Error('FileReader result is not a string'));
      }
    };
    reader.onerror = (e) => reject(e);
    reader.readAsText(fileBlob);
  });
};

export function removeIdentifierPattern(contents: string, marker: string) {
  const lines = contents.split('\n');
  const markerIndex = lines.findIndex(line => line.includes(marker));

  if (markerIndex !== -1) {
    const updatedLines = lines.slice(markerIndex + 1);
    return updatedLines.join('\n');
  } else {
    // Marker not found, return the original content
    return contents;
  }
}