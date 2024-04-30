"use client"
import Navigation from "@/components/Navigation";
import { useState, useEffect } from "react";
import { Upload } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { Button } from "@/components/ui/button";
import { MessageSquareMore } from 'lucide-react';
import Chat from "@/components/Chat";


const WS_BASE_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL;
const WS_URL = process.env.NEXT_PUBLIC_WB_SOCKET_URL;
const WAIT_TIME = process.env.NEXT_PUBLIC_WAIT_TIME;

export default function Home() {
  const [enableSend, setEnableSend] = useState(true);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [csv, setCsv] = useState<File | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<{sender: string, message: string}[]>([{
    "sender": "bot",
    "message": "Hello! Give me a brief explanation of what you are trying to achieve and what this data represents."
  }]);

  const [url, setUrl] = useState("");

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    // @ts-ignore
    accept: 'text/csv',
    onDrop: acceptedFiles => {
      // @ts-ignore
      setCsv(acceptedFiles[0]);
    }
  });

  useEffect(() => {
    if (csv && socket === null) {
      const socket = new WebSocket(WS_URL || 'ws://localhost:8000/ws');
  
    socket.addEventListener('message', (event) => {
      if (event.data.startsWith('PORT')) {
        console.log(WS_BASE_URL + ":" + event.data.split(":")[1]);
        setTimeout(() => {
          console.log("setting url");
          setUrl(WS_BASE_URL + ":" + event.data.split(":")[1]);
        }, parseInt(WAIT_TIME || "5000"));

      } else {
        setMessages((prev) => [...prev, {
          "sender": "bot",
          "message": event.data
        }]);
        setEnableSend(true);
      }
    });
  
    socket.addEventListener('open', () => {
      console.log('Connected to WebSocket');
      if (csv) {
        socket.send(csv);
      }
    });
  
    socket.addEventListener('close', () => {
      console.log('Disconnected from WebSocket');
    });
  
    setSocket(socket);
  
    // Cleanup function to close socket when component unmounts
    return () => {
      socket.close();
    };
    }
  
  }, [csv]);



  return (
    <div className="flex h-full w-full flex-col">
      <Navigation />

      <main className="flex flex-1 flex-col bg-muted/40">
        {
          !(csv && csv.name.endsWith(".csv")) ? (
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
              src={url}
              width="100%"
              height="100%"
            />
            </div>
            {!chatOpen ? 
            <Button className="rounded-full w-[80px] h-[80px] absolute bottom-6 right-6 p-3" onClick={() => setChatOpen(true)}>
              <MessageSquareMore className="h-[80%] w-[80%]"/>
              <span className="sr-only" onClick={() => setChatOpen(true)}>Send</span>
            </Button>: 
            <Chat 
            setOpen={setChatOpen} 
            setMessages={setMessages} 
            messages={messages} 
            socket={socket}
            setEnableSend={setEnableSend}
            enableSend={enableSend}/>
            }
            </>

            
            
          )
        }

      </main>
    </div>
  )
}

