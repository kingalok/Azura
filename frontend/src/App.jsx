import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Send, Bot, User, Settings, AlertCircle, CheckCircle } from 'lucide-react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [config, setConfig] = useState(null)
  const [projects, setProjects] = useState([])
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Check configuration status on load
    checkConfig()
    fetchProjects()
  }, [])

  const checkConfig = async () => {
    try {
      const response = await fetch('/api/config')
      const data = await response.json()
      setConfig(data)
    } catch (error) {
      console.error('Failed to check configuration:', error)
    }
  }

  const fetchProjects = async () => {
    try {
      const response = await fetch('/api/projects')
      if (response.ok) {
        const data = await response.json()
        setProjects(data.value || [])
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = { type: 'user', content: inputMessage, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      })

      const data = await response.json()
      
      if (data.success) {
        const botMessage = { 
          type: 'bot', 
          content: data.response, 
          timestamp: new Date() 
        }
        setMessages(prev => [...prev, botMessage])
      } else {
        const errorMessage = { 
          type: 'bot', 
          content: `Error: ${data.error}`, 
          timestamp: new Date(),
          isError: true
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      const errorMessage = { 
        type: 'bot', 
        content: `Failed to send message: ${error.message}`, 
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const addSampleMessage = (message) => {
    setInputMessage(message)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Azura - The Guardian of Pipelines
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Intelligent analysis of your Azure DevOps pipelines and builds
          </p>
        </div>

        {/* Configuration Status */}
        {config && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Configuration Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center gap-2">
                  {config.azure_devops_configured ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-red-500" />
                  )}
                  <span>Azure DevOps</span>
                  <Badge variant={config.azure_devops_configured ? "default" : "destructive"}>
                    {config.azure_devops_configured ? "Connected" : "Not Configured"}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  {config.azure_openai_configured ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-red-500" />
                  )}
                  <span>Azure OpenAI</span>
                  <Badge variant={config.azure_openai_configured ? "default" : "destructive"}>
                    {config.azure_openai_configured ? "Connected" : "Not Configured"}
                  </Badge>
                </div>
                {config.org_url && config.org_url !== "Not configured" && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Organization: {config.org_url}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Sample Questions */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Sample Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                "List the last 5 failed builds for my project",
                "Show me pipeline definitions for my Project",
                "Get logs for build 12345 in my Project",
                "Why did the latest build fail?",
                "Show me all builds from the last week",
                "What are the most common build failures?"
              ].map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="text-left h-auto p-3 whitespace-normal"
                  onClick={() => addSampleMessage(question)}
                >
                  {question}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Chat Interface */}
        <Card className="h-96">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              Chat with Agent
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col h-full">
            {/* Messages */}
            <ScrollArea className="flex-1 mb-4">
              <div className="space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                    Start a conversation by asking about your Azure Pipelines!
                  </div>
                )}
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-3 ${
                      message.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`flex gap-3 max-w-[80%] ${
                        message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
                      }`}
                    >
                      <div className="flex-shrink-0">
                        {message.type === 'user' ? (
                          <User className="h-6 w-6 text-blue-500" />
                        ) : (
                          <Bot className="h-6 w-6 text-green-500" />
                        )}
                      </div>
                      <div
                        className={`rounded-lg p-3 ${
                          message.type === 'user'
                            ? 'bg-blue-500 text-white'
                            : message.isError
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-100'
                        }`}
                      >
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        <div className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <Bot className="h-6 w-6 text-green-500" />
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="flex gap-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your Azure Pipelines..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Projects Info */}
        {projects.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Available Projects</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {projects.slice(0, 10).map((project) => (
                  <Badge key={project.id} variant="secondary">
                    {project.name}
                  </Badge>
                ))}
                {projects.length > 10 && (
                  <Badge variant="outline">
                    +{projects.length - 10} more
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default App

