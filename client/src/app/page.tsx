"use client"
import Navigation from "@/components/Navigation";
import { useState, useEffect } from "react";
import { Upload } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { Button } from "@/components/ui/button";
import { MessageSquareMore } from 'lucide-react';
import Chat from "@/components/Chat";

export default function Home() {

  const [csv, setCsv] = useState<File | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<{sender: string, message: string}[]>([{
    "sender": "bot",
    "message": "Hello! Give me a brief explanation of what you are trying to achieve and what this data represents."
  }]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    // @ts-ignore
    accept: 'text/csv',
    onDrop: acceptedFiles => {
      // @ts-ignore
      setCsv(acceptedFiles[0]);
    }
  });

  useEffect(() => {
    console.log(csv)
  }, [csv])



  const dashboard_url = "https://css4.pub/2015/icelandic/dictionary.pdf"

  return (
    <div className="flex h-full w-full flex-col">
      <Navigation />

      <main className="flex flex-1 flex-col bg-muted/40">
        {
          (csv && csv.name.endsWith(".csv")) ? (
            <div className="flex h-screen items-center justify-center">
              <div {...getRootProps()} className="flex flex-col items-center space-y-4 rounded-lg border-2 border-dashed border-gray-400 bg-white p-8 shadow-md dark:border-gray-600 dark:bg-gray-950">
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 text-gray-500 dark:text-gray-400" />
                <h3 className="mb-2 text-lg font-medium text-gray-900 dark:text-gray-50">
                  {isDragActive ? "Drop the files here ..." : "Drag and drop files here"}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">To get started!</p>
              {csv && (
                <p className="text-sm text-red-500">Please ensure the file is a CSV format.</p>
              )}
              </div>
            </div>

          ) : (
            <>
            <div className="w-[100vw] h-[94vh] p-0 m-0">
            <iframe
              src={dashboard_url}
              width="100%"
              height="100%"
            />
            </div>
            {!chatOpen ? 
            <Button className="rounded-full w-[80px] h-[80px] absolute bottom-6 right-6 p-3" onClick={() => setChatOpen(true)}>
              <MessageSquareMore className="h-[80%] w-[80%]"/>
              <span className="sr-only" onClick={() => setChatOpen(true)}>Send</span>
            </Button>:
            <Chat setOpen={setChatOpen} setMessages={setMessages} messages={messages}/>}
            </>
            
            
          )
        }

      </main>
    </div>
  )
}

