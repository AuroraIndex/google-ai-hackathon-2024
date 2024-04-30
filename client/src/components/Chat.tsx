import { Avatar } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { User, Bot, Send, CircleX } from 'lucide-react';
import Markdown from 'react-markdown';
import { useState, useEffect, useRef } from "react";

interface ChatProps {
    setOpen: (open: boolean) => void;
    setMessages: (messages: {sender: string, message: string}[]) => void;
    messages: {sender: string, message: string}[];
    socket: WebSocket | null;
    setEnableSend: (enableSend: boolean) => void;
    enableSend: boolean;
}


export default function Component({setOpen, setMessages, messages, socket, setEnableSend, enableSend}: ChatProps) {
    const [inputMessage, setInputMessage] = useState("");
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const userMessageComponent = (message: string, key?: string) => {
        return (
            <div className="flex items-center justify-end space-x-3" key={key}>
            <div className="max-w-[600px] rounded-lg bg-gray-900 p-3 text-sm text-gray-50 dark:bg-gray-50 dark:text-gray-900">
              <p className="break-words">{message}</p>
            </div>
            <Avatar className="h-8 w-8">
              <User />
            </Avatar>
          </div>
        
        )
    }

    const botMessageComponent = (message: string, key?: string) => {
        return (
            <div className="flex items-center space-x-3" key={key}>
            <Avatar className="h-8 w-8">
              <Bot />
            </Avatar>
            <div className="max-w-[32vw] rounded-lg bg-gray-100 p-3 text-sm dark:bg-gray-800 overflow-hidden">
              <Markdown className="break-words max-w-[32vw] overflow-auto">{message}</Markdown>
            </div>
          </div>
        )
    }

    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
      scrollToBottom();
  }, [messages]);

  const handleKeyPress = (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
          event.preventDefault();
          if (inputMessage.trim() && enableSend) {
              handleSendClick();
          }
      }
  };

  const handleSendClick = async () => {
    setEnableSend(false);
    // @ts-ignore
    setMessages(prevMessages => [...prevMessages, {sender: "user", message: inputMessage}]);
    setInputMessage("");
    console.log(socket)
    socket?.send(inputMessage);
}

  return (
    <div className="flex h-[80vh] w-[35vw] flex-col rounded-lg border border-gray-200 shadow-lg dark:border-gray-800 absolute bottom-6 right-6">
      <div className="flex items-center justify-between bg-gray-100 px-4 py-3 dark:bg-gray-800">
        <div className="flex items-center space-x-3">
          <Avatar className="h-8 w-8">
            <Bot />
          </Avatar>
          <h3 className="text-sm font-medium">Chat Bot</h3>
        </div>
        <Button size="icon" variant="ghost" onClick={() => setOpen(false)}>
          <CircleX className="h-7 w-7" />
        </Button>
      </div>
      <div className="flex-1 overflow-auto p-4 dark:bg-gray-900">
        <div className="space-y-4">
            {
                messages.map((message, index) => {
                    return message.sender === "user" ? userMessageComponent(message.message, index.toString()) : botMessageComponent(message.message, index.toString())
                })
            }
            <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="flex items-center space-x-2 border-t bg-gray-100 px-4 py-3 dark:bg-gray-800">
        <Input
          className="flex-1 rounded-md bg-white px-3 py-2 text-sm shadow-sm dark:bg-gray-950"
          placeholder="Type your message..."
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <Button size="icon" onClick={handleSendClick} disabled={!enableSend || inputMessage === ""}>
          <Send className="h-5 w-5" />
          <span className="sr-only">Send</span>
        </Button>
      </div>
    </div>
  )
}