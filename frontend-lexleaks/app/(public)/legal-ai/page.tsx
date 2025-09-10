'use client'

import { useState, useRef, useEffect } from 'react'
import { processLegalQuery, type LegalQueryResponse, type UserMsg, type AIMsg, type ChatState } from '@/lib/api'
import Navigation from '@/components/Navigation'
import TypewriterTitle from '@/components/TypewriterTitle'

export default function JurisBrainAIPage() {
  const [chatState, setChatState] = useState<ChatState>({
    sessionId: '',
    messages: [],
    memory: {
      scope: { jurisdiction: 'India', court: 'All Courts', date_range: '2010-Present' },
      facts: [],
      preferences: { style: 'detailed', export: 'PDF' }
    }
  })
  
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showReasoning, setShowReasoning] = useState<Record<string, boolean>>({})
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatState.messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: UserMsg = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    }

    // Add user message immediately
    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage]
    }))

    const query = inputValue.trim()
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await processLegalQuery({
        session_id: chatState.sessionId || undefined,
        message: {
          type: 'USER_QUERY',
          text: query,
          state_delta: {}
        }
      })

      // Create AI message from response
      const aiMessage: AIMsg = {
        id: `ai_${Date.now()}`,
        type: 'ai',
        turn_id: response.turn_id,
        answer: response.answer,
        reasoning_trail: response.reasoning_trail,
        citations: response.citations,
        followups: response.followups,
        timestamp: response.timestamp
      }

      // Update chat state with AI response and session info
      setChatState(prev => ({
        ...prev,
        sessionId: response.session_id,
        messages: [...prev.messages, aiMessage],
        memory: {
          ...prev.memory,
          scope: response.memory_update.scope || prev.memory.scope,
          facts: [...prev.memory.facts, ...response.memory_update.facts].slice(-10) // Keep last 10 facts
        }
      }))

    } catch (error) {
      console.error('Error processing query:', error)
      // Add error message
      const errorMessage: AIMsg = {
        id: `error_${Date.now()}`,
        type: 'ai',
        turn_id: 'error',
        answer: {
          summary: 'Error occurred',
          text: 'Sorry, I encountered an error processing your query. Please try again.',
          confidence: 'low'
        },
        reasoning_trail: [],
        citations: [],
        followups: ['Try again', 'Simplify your question'],
        timestamp: new Date().toISOString()
      }
      
      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage]
      }))
    } finally {
      setIsLoading(false)
    }
  }

  const handleFollowUpClick = (followUpText: string) => {
    // Map follow-up text to structured actions
    let action = "RETRY_LAST"
    let type = "FOLLOWUP"
    
    if (followUpText.toLowerCase().includes("try again")) {
      action = "RETRY_LAST"
    } else if (followUpText.toLowerCase().includes("simplify")) {
      action = "SIMPLIFY_ANSWER"
    } else if (followUpText.toLowerCase().includes("narrow") || followUpText.toLowerCase().includes("supreme court")) {
      action = "NARROW_TO_SC"
    } else if (followUpText.toLowerCase().includes("widen") || followUpText.toLowerCase().includes("all courts")) {
      action = "WIDEN_SCOPE"
    } else if (followUpText.toLowerCase().includes("more details") || followUpText.toLowerCase().includes("expand")) {
      action = "EXPAND_ANSWER"
    }
    
    // Send structured action instead of plain text
    handleStructuredAction(type, action, followUpText)
  }

  const handleStructuredAction = async (type: string, action: string, displayText: string) => {
    setIsLoading(true)
    
    try {
      // Add user message for display
      const userMessage: UserMsg = {
        id: Date.now().toString(),
        type: 'user',
        content: displayText,
        timestamp: new Date().toISOString()
      }
      
      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage]
      }))
      
      // Send structured action to backend
      const response = await processLegalQuery({
        session_id: chatState.sessionId,
        message: {
          type: type,
          action: action,
          text: null,
          state_delta: {}
        }
      })
      
      if (response.success) {
        const aiMessage: AIMsg = {
          id: response.turn_id,
          type: 'ai',
          turn_id: response.turn_id,
          answer: {
            summary: response.answer.summary,
            text: response.answer.text,
            confidence: response.answer.confidence
          },
          reasoning_trail: response.reasoning_trail,
          citations: response.citations,
          followups: response.followups,
          timestamp: response.timestamp
        }
        
        setChatState(prev => ({
          ...prev,
          sessionId: response.session_id,
          messages: [...prev.messages, aiMessage],
          memory: {
            ...prev.memory,
            ...response.memory_update
          }
        }))
      } else {
        // Handle error
        const errorMessage: AIMsg = {
          id: Date.now().toString(),
          type: 'ai',
          turn_id: `error_${Date.now()}`,
          answer: {
            summary: "Error occurred",
            text: response.error || "Sorry, I encountered an error processing your request.",
            confidence: "low"
          },
          reasoning_trail: [],
          citations: [],
          followups: ["Try again", "Simplify your question"],
          timestamp: new Date().toISOString()
        }
        
        setChatState(prev => ({
          ...prev,
          messages: [...prev.messages, errorMessage]
        }))
      }
    } catch (error) {
      console.error('Error processing structured action:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleReasoning = (messageId: string) => {
    setShowReasoning(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section - Matching Main Site */}
      <header className="main-header parallax-container">
        <TypewriterTitle text="JURISBRAIN AI" className="main-title" delay={150} />
        <p className="main-subtitle">Your Legal Research Copilot.</p>
      </header>

      <Navigation currentPage="/legal-ai" />

      {/* Session Info */}
      {chatState.sessionId && (
        <div className="mb-8">
          <div className="case-file text-center">
            <span>Session: {chatState.sessionId.slice(0, 8)}...</span>
            {' | '}
            <span>Messages: {chatState.messages.length}</span>
            {' | '}
            <span>Scope: {chatState.memory.scope.jurisdiction} • {chatState.memory.scope.court}</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main>
        <div className="article-card">
          {/* Chat Container */}
          <div className="h-[600px] overflow-y-auto p-6 space-y-6">
            {chatState.messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-8xl mb-6">⚖️</div>
                  <h3 className="article-title text-3xl md:text-4xl leading-tight mb-4">
                    Welcome to JurisBrain AI
                  </h3>
                  <p className="article-excerpt mb-6 max-w-md mx-auto">
                    Ask any legal question and get comprehensive research with citations, case law, and follow-up suggestions.
                  </p>
                  <div className="bg-brand-light/20 dark:bg-brand-dark/30 border border-brand-accent/30 rounded-lg p-4 text-left max-w-md mx-auto">
                    <h4 className="font-display font-semibold text-brand-dark dark:text-brand-light mb-2">Try these examples:</h4>
                    <ul className="text-sm text-brand-muted dark:text-brand-light/70 space-y-1">
                      <li>• "What is defamation in Indian law?"</li>
                      <li>• "Explain Article 21 of the Constitution"</li>
                      <li>• "What are the recent developments in privacy law?"</li>
                      <li>• "How does the new criminal code affect bail provisions?"</li>
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              chatState.messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                    {message.type === 'user' ? (
                      <UserBubble message={message} />
                    ) : (
                      <AIBubble 
                        message={message} 
                        showReasoning={showReasoning[message.id] || false}
                        onToggleReasoning={() => toggleReasoning(message.id)}
                        onFollowUpClick={handleFollowUpClick}
                      />
                    )}
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%]">
                  <AILoadingBubble />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-brand-accent/20 p-6">
            <div className="flex space-x-4">
              <div className="flex-1">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a legal question..."
                  className="w-full px-4 py-3 border border-brand-accent/30 rounded-lg focus:ring-2 focus:ring-brand-accent focus:border-brand-accent resize-none bg-white dark:bg-brand-dark/50 text-brand-dark dark:text-brand-light placeholder-brand-muted/60"
                  rows={2}
                  disabled={isLoading}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="brand-button disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {isLoading ? 'Researching...' : 'Send'}
              </button>
            </div>
            <div className="mt-3 text-sm text-brand-muted dark:text-brand-light/70">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

// User Message Bubble
function UserBubble({ message }: { message: UserMsg }) {
  return (
    <div className="bg-[#8B0000] dark:bg-[#d4766f] text-white rounded-lg px-6 py-4 max-w-full shadow-md">
      <div className="whitespace-pre-wrap font-medium text-white">{message.content}</div>
      <div className="text-xs text-white/80 mt-2 opacity-75">
        {new Date(message.timestamp).toLocaleTimeString()}
      </div>
    </div>
  )
}

// AI Message Bubble
function AIBubble({ 
  message, 
  showReasoning, 
  onToggleReasoning, 
  onFollowUpClick 
}: { 
  message: AIMsg
  showReasoning: boolean
  onToggleReasoning: () => void
  onFollowUpClick: (text: string) => void
}) {
  return (
    <div className="bg-brand-light/30 dark:bg-brand-dark/30 border border-brand-accent/20 rounded-lg p-6 max-w-full shadow-md">
      {/* Answer Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-brand-accent rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">⚖️</span>
          </div>
          <div>
            <span className="text-lg font-display font-bold text-brand-dark dark:text-brand-light">JurisBrain AI</span>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                message.answer.confidence === 'high' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : message.answer.confidence === 'medium'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {message.answer.confidence} confidence
              </span>
            </div>
          </div>
        </div>
        <div className="text-sm text-brand-muted dark:text-brand-light/70">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
      
      {/* Answer Content */}
      <div className="mb-6">
        <div className="prose prose-lg max-w-none text-brand-dark dark:text-brand-light leading-relaxed">
          <div className="whitespace-pre-wrap">
            {message.answer.text.split('\n').map((line, index) => {
              // Handle bold text formatting
              if (line.includes('**') && line.includes(':**')) {
                const parts = line.split('**')
                return (
                  <div key={index} className="mb-2">
                    <strong className="text-brand-accent">{parts[1]}</strong>
                    {parts.slice(2).join('')}
                  </div>
                )
              }
              // Handle bullet points
              if (line.trim().startsWith('* ')) {
                return (
                  <div key={index} className="ml-4 mb-1">
                    • {line.trim().substring(2)}
                  </div>
                )
              }
              // Handle numbered lists
              if (line.trim().match(/^\d+\./)) {
                return (
                  <div key={index} className="ml-4 mb-2">
                    {line.trim()}
                  </div>
                )
              }
              // Regular paragraphs
              if (line.trim()) {
                return (
                  <div key={index} className="mb-2">
                    {line}
                  </div>
                )
              }
              // Empty lines
              return <div key={index} className="mb-2"></div>
            })}
          </div>
        </div>
      </div>

      {/* Citations */}
      {message.citations.length > 0 && (
        <div className="mb-6">
          <div className="text-sm font-display font-semibold text-brand-dark dark:text-brand-light mb-3">
            Sources & Citations:
          </div>
          <div className="flex flex-wrap gap-2">
            {message.citations.map((citation) => (
              <button
                key={citation.pin}
                className="px-3 py-1 text-sm bg-brand-accent/10 dark:bg-brand-accent/20 text-brand-accent dark:text-brand-accent rounded-full hover:bg-brand-accent/20 dark:hover:bg-brand-accent/30 transition-colors border border-brand-accent/30"
                title={`${citation.title} - ${citation.court_or_source}`}
              >
                [{citation.pin}] {citation.type === 'case' ? 'Case Law' : 'Web Source'}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Reasoning Trail */}
      <div className="mb-6">
        <button
          onClick={onToggleReasoning}
          className="text-sm text-brand-accent dark:text-brand-accent hover:underline font-medium"
        >
          {showReasoning ? '▼ Hide' : '▶ Show'} Reasoning Trail
        </button>
        
        {showReasoning && (
          <div className="mt-3 space-y-3">
            {message.reasoning_trail.map((step, index) => (
              <div key={index} className="bg-brand-light/20 dark:bg-brand-dark/40 border border-brand-accent/20 p-4 rounded-lg">
                <div className="font-display font-semibold text-brand-dark dark:text-brand-light mb-1">{step.step}</div>
                <div className="text-sm text-brand-muted dark:text-brand-light/80">{step.notes}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Follow-up Questions */}
      {message.followups && message.followups.length > 0 && (
        <div className="mt-4">
          <div className="text-sm font-display font-semibold text-brand-dark dark:text-brand-light mb-3">
            Follow-up questions:
          </div>
          <div className="flex flex-wrap gap-2">
            {message.followups.map((followup, index) => (
              <button
                key={index}
                onClick={() => onFollowUpClick(followup)}
                className="px-4 py-2 text-sm bg-brand-accent/10 dark:bg-brand-accent/20 text-brand-accent dark:text-brand-accent rounded-full hover:bg-brand-accent/20 dark:hover:bg-brand-accent/30 transition-colors border border-brand-accent/30 font-medium cursor-pointer"
              >
                {followup}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// AI Loading Bubble
function AILoadingBubble() {
  return (
    <div className="bg-brand-light/30 dark:bg-brand-dark/30 border border-brand-accent/20 rounded-lg p-6">
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-8 h-8 bg-brand-accent rounded-full flex items-center justify-center">
          <span className="text-white font-bold text-sm">⚖️</span>
        </div>
        <div>
          <span className="text-lg font-display font-bold text-brand-dark dark:text-brand-light">JurisBrain AI</span>
          <div className="flex space-x-1 mt-1">
            <div className="w-2 h-2 bg-brand-accent rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-brand-accent rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-brand-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
      </div>
      <div className="text-brand-muted dark:text-brand-light/80">
        Analyzing your question and researching legal sources...
      </div>
    </div>
  )
}