import { Avatar } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { User, Bot, Send, CircleX } from 'lucide-react';

import { useState, useEffect, useRef } from "react";

interface ChatProps {
    setOpen: (open: boolean) => void;
    setMessages: (messages: {sender: string, message: string}[]) => void;
    messages: {sender: string, message: string}[];
}




export default function Component({setOpen, setMessages, messages}: ChatProps) {
    const [sendMessage, setSendMessage] = useState("");
    const [enableSend, setEnableSend] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const userMessageComponent = (message: string) => {
        return (
            <div className="flex items-center justify-end space-x-3">
            <div className="max-w-[280px] rounded-lg bg-gray-900 p-3 text-sm text-gray-50 dark:bg-gray-50 dark:text-gray-900">
              <p className="break-words">{message}</p>
            </div>
            <Avatar className="h-8 w-8">
              <User />
            </Avatar>
          </div>
        
        )
    }

    const botMessageComponent = (message: string) => {
        return (
            <div className="flex items-center space-x-3">
            <Avatar className="h-8 w-8">
              <Bot />
            </Avatar>
            <div className="max-w-[280px] rounded-lg bg-gray-100 p-3 text-sm dark:bg-gray-800">
              <p className="break-words">{message}</p>
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
          if (sendMessage.trim() && enableSend) {
              handleSendClick();
          }
      }
  };

  const handleSendClick = async () => {
    setEnableSend(false);
    // @ts-ignore
    setMessages(prevMessages => [...prevMessages, {sender: "user", message: sendMessage}]);
    setSendMessage("");

    const newMessage = await new Promise(resolve => setTimeout(() => {
        resolve({
          sender: "bot",
          message: "Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!"
        });
    }, 1000));
    // @ts-ignore
    setMessages(prevMessages => [...prevMessages, newMessage as { sender: string; message: string }]);
    setEnableSend(true);
}

  return (
    <div className="flex h-[600px] w-[400px] flex-col rounded-lg border border-gray-200 shadow-lg dark:border-gray-800 absolute bottom-6 right-6">
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
                    return message.sender === "user" ? userMessageComponent(message.message) : botMessageComponent(message.message)
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
          value={sendMessage}
          onChange={(e) => setSendMessage(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <Button size="icon" onClick={handleSendClick} disabled={!enableSend || sendMessage === ""}>
          <Send className="h-5 w-5" />
          <span className="sr-only">Send</span>
        </Button>
      </div>
    </div>
  )
}