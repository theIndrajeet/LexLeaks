'use client'

import { useState, useRef, useEffect } from 'react'
import { processLegalQuery, type LegalQueryResponse, type UserMsg, type AIMsg, type ChatState, sendChatMessage, getChatMessages, createChatWebSocket, handleChatAction, type ChatMessage, type ChatRequest, startEventDrivenResearch, getEventDrivenResearchStatus, getEventDrivenResearchResults, type EventDrivenResearchRequest, type EventDrivenResearchResponse, type EventDrivenResearchStatus } from '@/lib/api'
import Navigation from '@/components/Navigation'
import TypewriterTitle from '@/components/TypewriterTitle'

// Types for Deep Research
interface ResearchProgress {
  research_id: string
  overall_progress: number
  current_phase: string
  current_activity: string
  elapsed_time: string
  remaining_time: string
  estimated_completion: string
  is_completed: boolean
  has_errors: boolean
  phases: Array<{
    name: string
    status: 'pending' | 'in_progress' | 'completed' | 'failed'
    progress: number
  }>
}

interface DeepResearchRequest {
  topic: string
  jurisdictions: string[]
  depth_level: 'quick' | 'comprehensive' | 'exhaustive'
  audience: 'legal_professional' | 'student' | 'general'
  focus_areas?: string[]
  timeline?: string
  output_format?: string
  additional_requirements?: string
  word_count?: number
}

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
  
  // New chat session state
  const [chatSessionId, setChatSessionId] = useState<string | null>(null)
  const [websocket, setWebsocket] = useState<WebSocket | null>(null)
  
  // Deep Research State
  const [researchMode, setResearchMode] = useState<'chat' | 'deep'>('chat')
  const [researchProgress, setResearchProgress] = useState<ResearchProgress | null>(null)
  const [researchContent, setResearchContent] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'Sources' | 'Progress'>('Sources')
  const [isRightPanelCollapsed, setIsRightPanelCollapsed] = useState(false)
  const [currentResearchId, setCurrentResearchId] = useState<string | null>(null)
  const [multiAgentResearchId, setMultiAgentResearchId] = useState<string | null>(null)
  const [multiAgentStatus, setMultiAgentStatus] = useState<any>(null)
  const [multiAgentOutput, setMultiAgentOutput] = useState<any>(null)
  const [researchRequest, setResearchRequest] = useState<DeepResearchRequest>({
    topic: '',
    jurisdictions: ['India'],
    depth_level: 'comprehensive',
    audience: 'legal_professional',
    focus_areas: [],
    word_count: 50000
  })
  const [showDeepResearchForm, setShowDeepResearchForm] = useState(false)
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatState.messages])

  // Cleanup progress interval on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
      }
    }
  }, [])

  // Deep Research Functions
  const startDeepResearchWithRequest = async (request: DeepResearchRequest) => {
    if (!request.topic.trim()) return

    try {
      setIsLoading(true)
      // Reset content and progress when starting new research
      setResearchContent(null)
      setResearchProgress(null)
      
      // Convert to event-driven research request
      const eventDrivenRequest: EventDrivenResearchRequest = {
        topic: request.topic,
        jurisdictions: request.jurisdictions,
        depth_level: request.depth_level,
        audience: request.audience,
        focus_areas: request.focus_areas || ['statutory_law', 'case_law', 'enforcement', 'judicial_interpretation', 'amendments', 'comparative_analysis']
      }
      
      const data = await startEventDrivenResearch(eventDrivenRequest)
      
      if (data.success) {
        setResearchMode('deep')
        setShowDeepResearchForm(false)
        setCurrentResearchId(data.run_id)
        
        // Start polling for progress
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current)
        }
        
        progressIntervalRef.current = setInterval(async () => {
          try {
            const progressData = await getEventDrivenResearchStatus(data.run_id)
            // Convert to ResearchProgress format
            const convertedProgress: ResearchProgress = {
              research_id: data.run_id,
              overall_progress: progressData.progress_percentage,
              current_phase: progressData.current_phase,
              current_activity: progressData.current_phase,
              elapsed_time: "calculating...",
              remaining_time: progressData.estimated_completion,
              estimated_completion: progressData.estimated_completion,
              is_completed: progressData.status === 'completed',
              has_errors: false,
              phases: []
            }
            setResearchProgress(convertedProgress)
            
            // Also try to fetch content if available
            try {
              const contentData = await getEventDrivenResearchResults(data.run_id)
              if (contentData.success && contentData.results) {
                setResearchContent(contentData.results)
              }
            } catch (contentError) {
              // Content not ready yet, continue polling
            }
            
            if (convertedProgress.is_completed) {
              if (progressIntervalRef.current) {
                clearInterval(progressIntervalRef.current)
              }
              // Final attempt to get content
              try {
                const contentData = await getEventDrivenResearchResults(data.run_id)
                if (contentData.success && contentData.results) {
                  setResearchContent(contentData.results)
                }
              } catch (contentError) {
                console.error('Error fetching final content:', contentError)
              }
            }
          } catch (error) {
            console.error('Error fetching progress:', error)
          }
        }, 2000) // Poll every 2 seconds
      }
    } catch (error) {
      console.error('Error starting deep research:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const startDeepResearch = async () => {
    await startMultiAgentResearch()
  }

  const connectToResearch = async (researchId: string) => {
    try {
      setCurrentResearchId(researchId)
      setResearchMode('deep')
      
      // Start polling for this research
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
      }
      
      progressIntervalRef.current = setInterval(async () => {
        try {
          const progressResponse = await fetch(`http://localhost:8000/api/deep-research/progress/${researchId}`)
          const progressData = await progressResponse.json()
          setResearchProgress(progressData)
          
          // Also try to fetch content if available
          try {
            const contentResponse = await fetch(`http://localhost:8000/api/deep-research/content/${researchId}`)
            const contentData = await contentResponse.json()
            if (contentData.success && contentData.content) {
              setResearchContent(contentData.content)
            }
          } catch (contentError) {
            // Content not ready yet, continue polling
          }
          
          if (progressData.is_completed) {
            if (progressIntervalRef.current) {
              clearInterval(progressIntervalRef.current)
            }
            // Final attempt to get content
            try {
              const contentResponse = await fetch(`http://localhost:8000/api/deep-research/content/${researchId}`)
              const contentData = await contentResponse.json()
              if (contentData.success && contentData.content) {
                setResearchContent(contentData.content)
              }
            } catch (contentError) {
              console.error('Error fetching final content:', contentError)
            }
          }
        } catch (error) {
          console.error('Error fetching progress:', error)
        }
      }, 2000) // Poll every 2 seconds
    } catch (error) {
      console.error('Error connecting to research:', error)
    }
  }

  const stopDeepResearch = () => {
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current)
    }
    setResearchMode('chat')
    setResearchProgress(null)
    setResearchContent(null)
    setShowDeepResearchForm(false)
  }

  // Multi-Agent Research Functions
  const startMultiAgentResearch = async () => {
    if (!researchRequest.topic.trim()) return

    try {
      setIsLoading(true)
      
      // Calculate number of agents based on word count
      const wordCount = researchRequest.word_count || 50000
      const wordsPerAgent = 2500
      const numAgents = Math.max(1, Math.min(20, Math.ceil(wordCount / wordsPerAgent)))
      
      const requestWithAgents = {
        ...researchRequest,
        num_agents: numAgents,
        words_per_agent: Math.ceil(wordCount / numAgents)
      }
      
      const response = await fetch('http://localhost:8000/api/multi-agent-research/start-research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestWithAgents),
      })

      const data = await response.json()
      
      if (data.success) {
        setMultiAgentResearchId(data.research_id)
        setResearchMode('deep')
        
        // Start polling for multi-agent research status
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current)
        }
        
        progressIntervalRef.current = setInterval(async () => {
          try {
            const statusResponse = await fetch(`http://localhost:8000/api/multi-agent-research/status/${data.research_id}`)
            const statusData = await statusResponse.json()
            setMultiAgentStatus(statusData)
            
            // Try to get output if completed
            if (statusData.status === 'completed') {
              try {
                const outputResponse = await fetch(`http://localhost:8000/api/multi-agent-research/output/${data.research_id}`)
                const outputData = await outputResponse.json()
                if (outputData.final_output) {
                  setMultiAgentOutput(outputData)
                }
              } catch (outputError) {
                console.error('Error fetching multi-agent output:', outputError)
              }
              
              if (progressIntervalRef.current) {
                clearInterval(progressIntervalRef.current)
              }
            }
          } catch (error) {
            console.error('Error fetching multi-agent status:', error)
          }
        }, 3000) // Poll every 3 seconds
      }
    } catch (error) {
      console.error('Error starting multi-agent research:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const query = inputValue.trim()
    setInputValue('')
    setIsLoading(true)

    try {
      // Send message to new chat API
      const response = await sendChatMessage({
        session_id: chatSessionId || undefined,
        message: query,
        message_type: 'user_query'
      })

      // Update session ID if this is a new session
      if (!chatSessionId) {
        setChatSessionId(response.session_id)
        
        // Set up WebSocket connection for real-time updates
        const ws = createChatWebSocket(response.session_id)
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'new_message') {
            const newMessage = data.data
            setChatState(prev => ({
              ...prev,
              messages: [...prev.messages, newMessage]
            }))
          }
        }
        setWebsocket(ws)
      }

      // Convert new chat message to legacy format for compatibility
      const userMessage: UserMsg = {
        id: `user_${Date.now()}`,
        type: 'user',
        content: query,
        timestamp: new Date().toISOString()
      }

      const aiMessage: AIMsg = {
        id: response.message.id,
        type: 'ai',
        turn_id: response.message_id,
        answer: {
          summary: response.message.content.substring(0, 100) + '...',
          text: response.message.content,
          confidence: 'high'
        },
        reasoning_trail: response.message.reasoning_trail || [],
        citations: (response.message.citations || []).map(citation => ({
          pin: citation.pin_number,
          type: citation.type === 'case' ? 'case' : 'web',
          title: citation.title,
          court_or_source: citation.court_or_source,
          date: citation.date,
          url: citation.url,
          snippet: '',
          lines: '',
          weight: 'secondary' as const
        })),
        followups: response.message.followup_questions || [],
        timestamp: response.message.timestamp
      }

      // Update chat state
      setChatState(prev => ({
        ...prev,
        sessionId: response.session_id,
        messages: [...prev.messages, userMessage, aiMessage]
      }))

      // If this is a research plan message, show research progress
      if (response.message.type === 'research_plan' && response.message.research_id) {
        setResearchProgress({
          research_id: response.message.research_id,
          overall_progress: 0,
          current_phase: 'planning',
          current_activity: 'Creating research outline...',
          elapsed_time: '0m',
          remaining_time: '45-90m',
          estimated_completion: new Date(Date.now() + 90 * 60000).toISOString(),
          is_completed: false,
          has_errors: false,
          phases: [
            { name: 'Planning', progress: 0, status: 'in_progress' },
            { name: 'Source Discovery', progress: 0, status: 'pending' },
            { name: 'Extraction', progress: 0, status: 'pending' },
            { name: 'Writing', progress: 0, status: 'pending' },
            { name: 'QA', progress: 0, status: 'pending' },
            { name: 'Export', progress: 0, status: 'pending' }
          ]
        })
      }

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
    let action: 'RETRY_LAST' | 'WIDEN_SCOPE' | 'NARROW_TO_SC' | 'ADD_CONTEXT' | 'SIMPLIFY_ANSWER' | 'EXPAND_ANSWER' | undefined = undefined
    let type: 'USER_QUERY' | 'FOLLOWUP' | 'SCOPE_UPDATE' | 'UI_EVENT' | 'META' = "FOLLOWUP"
    
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
    } else {
      // For unrecognized follow-ups, treat as a new user query
      type = "USER_QUERY"
      action = undefined
    }
    
    // Send structured action instead of plain text
    handleStructuredAction(type, action, followUpText)
  }

  const handleStructuredAction = async (type: 'USER_QUERY' | 'FOLLOWUP' | 'SCOPE_UPDATE' | 'UI_EVENT' | 'META', action: 'RETRY_LAST' | 'WIDEN_SCOPE' | 'NARROW_TO_SC' | 'ADD_CONTEXT' | 'SIMPLIFY_ANSWER' | 'EXPAND_ANSWER' | undefined, displayText: string) => {
    setIsLoading(true)
    
    try {
      // Check if we're trying to retry but there's no previous query
      if (action === "RETRY_LAST" && (!chatState.messages || chatState.messages.length === 0)) {
        console.warn("Cannot retry: No previous query found")
        setIsLoading(false)
        return
      }
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
          text: displayText,
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
    <div className="h-screen flex flex-col bg-[#F8F7F4] dark:bg-[#0F172A]">
      {/* Header - Compact */}
      <header className="border-b border-[#64748B]/20 bg-white dark:bg-[#111827] px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#111827] dark:text-white tracking-tight">
              Deep Research by JurisBrain
            </h1>
            <p className="text-sm text-[#475569] dark:text-[#64748B] mt-1">
              Commission a 50–100+ page legal report
            </p>
          </div>
          <Navigation currentPage="/legal-ai" className="!mb-0" />
        </div>
      </header>


      {/* Main Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Chat Thread (65%) */}
        <div className="flex-1 flex flex-col">
          {/* Chat Container */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {chatState.messages.length === 0 && !researchProgress && !researchContent ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-2xl">
                  <div className="text-6xl mb-6"></div>
                  <h2 className="text-3xl font-bold text-[#111827] dark:text-white mb-4">
                    Commission a 50–100+ page legal report
                  </h2>
                  <p className="text-lg text-[#475569] dark:text-[#64748B] mb-8">
                    Plan → Source → Extract → Write → QA → Export. Fully cited. Reproducible.
                  </p>
                  
                  {/* Quick Start Templates */}
                  
                  <div className="grid grid-cols-2 gap-4 mb-8">
                    <button 
                      onClick={async () => {
                        const newRequest = {
                          topic: "Analyze competition law in India",
                          jurisdictions: ["India"],
                          depth_level: "comprehensive" as const,
                          audience: "legal_professional" as const,
                          focus_areas: ["statutory_law", "case_law"],
                          timeline: "recent_5_years",
                          output_format: "detailed_report",
                          additional_requirements: "Focus on CCI decisions and market dynamics"
                        }
                        setResearchRequest(newRequest)
                        // Start research with the new request directly
                        await startDeepResearchWithRequest(newRequest)
                      }}
                      className="p-4 bg-white dark:bg-[#111827] border border-[#64748B]/20 rounded-xl hover:shadow-lg transition-all text-left"
                    >
                      <div className="font-semibold text-[#111827] dark:text-white">Competition Law</div>
                      <div className="text-sm text-[#475569] dark:text-[#64748B]">CCI decisions & market dynamics</div>
                    </button>
                    <button 
                      onClick={async () => {
                        const newRequest = {
                          topic: "Data privacy laws India vs EU",
                          jurisdictions: ["India", "EU"],
                          depth_level: "comprehensive" as const,
                          audience: "legal_professional" as const,
                          focus_areas: ["statutory_law", "case_law"],
                          timeline: "recent_5_years",
                          output_format: "detailed_report",
                          additional_requirements: "Compare GDPR vs DPDPA"
                        }
                        setResearchRequest(newRequest)
                        await startDeepResearchWithRequest(newRequest)
                      }}
                      className="p-4 bg-white dark:bg-[#111827] border border-[#64748B]/20 rounded-xl hover:shadow-lg transition-all text-left"
                    >
                      <div className="font-semibold text-[#111827] dark:text-white">Data Privacy</div>
                      <div className="text-sm text-[#475569] dark:text-[#64748B]">GDPR vs DPDPA analysis</div>
                    </button>
                    <button 
                      onClick={async () => {
                        const newRequest = {
                          topic: "Corporate M&A due diligence",
                          jurisdictions: ["India"],
                          depth_level: "comprehensive" as const,
                          audience: "legal_professional" as const,
                          focus_areas: ["statutory_law", "case_law"],
                          timeline: "recent_5_years",
                          output_format: "detailed_report",
                          additional_requirements: "Focus on regulatory approvals and compliance"
                        }
                        setResearchRequest(newRequest)
                        await startDeepResearchWithRequest(newRequest)
                      }}
                      className="p-4 bg-white dark:bg-[#111827] border border-[#64748B]/20 rounded-xl hover:shadow-lg transition-all text-left"
                    >
                      <div className="font-semibold text-[#111827] dark:text-white">Corporate/M&A</div>
                      <div className="text-sm text-[#475569] dark:text-[#64748B]">Regulatory approvals</div>
                    </button>
                    <button 
                      onClick={async () => {
                        const newRequest = {
                          topic: "Intellectual property enforcement",
                          jurisdictions: ["India"],
                          depth_level: "comprehensive" as const,
                          audience: "legal_professional" as const,
                          focus_areas: ["statutory_law", "case_law"],
                          timeline: "recent_5_years",
                          output_format: "detailed_report",
                          additional_requirements: "Focus on patent and trademark enforcement"
                        }
                        setResearchRequest(newRequest)
                        await startDeepResearchWithRequest(newRequest)
                      }}
                      className="p-4 bg-white dark:bg-[#111827] border border-[#64748B]/20 rounded-xl hover:shadow-lg transition-all text-left"
                    >
                      <div className="font-semibold text-[#111827] dark:text-white">IP Law</div>
                      <div className="text-sm text-[#475569] dark:text-[#64748B]">Patent & trademark analysis</div>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {/* Show chat messages if any */}
                {chatState.messages.map((message) => (
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
                ))}
                
                {/* Show research content in main area when research is active */}
                {(researchProgress || researchContent) && (
                  <div className="bg-white dark:bg-[#111827] border border-[#64748B]/20 rounded-xl p-6">
                    <h3 className="text-xl font-bold text-[#111827] dark:text-white mb-4">
                       Research Report: {researchRequest.topic}
                    </h3>
                    
                    {researchContent?.executive_summary && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-[#111827] dark:text-white mb-2">Executive Summary</h4>
                        <div className="text-sm text-[#475569] dark:text-[#64748B]">
                          <div dangerouslySetInnerHTML={{ __html: researchContent.executive_summary.replace(/\n/g, '<br>') }} />
                        </div>
                      </div>
                    )}
                    
                    {researchContent?.legal_framework_analysis && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-[#111827] dark:text-white mb-2">Legal Framework Analysis</h4>
                        <div className="text-sm text-[#475569] dark:text-[#64748B]">
                          <div dangerouslySetInnerHTML={{ __html: researchContent.legal_framework_analysis.replace(/\n/g, '<br>') }} />
                        </div>
                      </div>
                    )}
                    
                    {researchContent?.case_law_synthesis && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-[#111827] dark:text-white mb-2">Case Law Synthesis</h4>
                        <div className="text-sm text-[#475569] dark:text-[#64748B]">
                          <div dangerouslySetInnerHTML={{ __html: researchContent.case_law_synthesis.replace(/\n/g, '<br>') }} />
                        </div>
                      </div>
                    )}
                    
                    {researchProgress && !researchContent && (
                      <div className="flex items-center gap-2 text-[#475569] dark:text-[#64748B]">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#3FA796]"></div>
                        <span>Generating research report...</span>
                      </div>
                    )}
                  </div>
                )}
              </>
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

          {/* Composer - Sticky */}
          <div className="border-t border-[#64748B]/20 bg-white dark:bg-[#111827] p-6">
            <div className="max-w-4xl mx-auto">
              {/* Progress Bar - Moved here from top */}
              {researchProgress && (
                <div className="mb-4">
                  <div className="flex items-center space-x-6">
                    {['Planning', 'Sources', 'Extraction', 'Writing', 'QA', 'Export'].map((phase, index) => (
                      <div key={phase} className="flex items-center space-x-2">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                          index < 2 ? 'bg-[#3FA796] text-white' : 
                          index === 2 ? 'bg-[#D97706] text-white' : 
                          'bg-[#64748B]/30 text-[#64748B]'
                        }`}>
                          {index < 2 ? '✓' : index + 1}
                        </div>
                        <span className={`text-sm font-medium ${
                          index <= 2 ? 'text-[#111827] dark:text-white' : 'text-[#64748B]'
                        }`}>
                          {phase}
                        </span>
                      </div>
                    ))}
                    <div className="flex items-center space-x-2 text-sm text-[#64748B]">
                      <div className="w-24 bg-[#64748B]/20 rounded-full h-2">
                        <div 
                          className="bg-[#D97706] h-2 rounded-full transition-all duration-300"
                          style={{ width: `${researchProgress.overall_progress}%` }}
                        />
                      </div>
                      <span>{researchProgress.overall_progress}%</span>
                      <span>• {researchProgress.remaining_time} left</span>
                    </div>
                  </div>
                </div>
              )}
              <div className="flex space-x-4">
                <div className="flex-1">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask or paste your brief—Deep Research will plan and run live"
                    className="w-full px-4 py-3 border border-[#64748B]/30 rounded-xl focus:ring-2 focus:ring-[#C46A5A] focus:border-[#C46A5A] resize-none bg-white dark:bg-[#111827] text-[#111827] dark:text-white placeholder-[#475569]/60"
                    rows={2}
                    disabled={isLoading}
                  />
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="bg-[#C46A5A] hover:bg-[#B85A4A] text-white px-6 py-3 rounded-xl font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Researching...' : 'Send'}
                </button>
              </div>
              <div className="mt-2 text-sm text-[#475569] dark:text-[#64748B]">
                Press Enter to send, Shift+Enter for new line • Cmd+K to go to section
              </div>
            </div>
          </div>
        </div>

        {/* Right: Docked Console (35%) */}
        <div className={`${isRightPanelCollapsed ? 'w-12' : 'w-[35%]'} border-l border-[#64748B]/20 bg-white dark:bg-[#111827] flex flex-col transition-all duration-300`}>
          {/* Collapse/Expand Button */}
          <div className="border-b border-[#64748B]/20 px-3 py-3">
            <button
              onClick={() => setIsRightPanelCollapsed(!isRightPanelCollapsed)}
              className="w-6 h-6 flex items-center justify-center text-[#64748B] hover:text-[#111827] dark:hover:text-white transition-colors"
            >
              {isRightPanelCollapsed ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              )}
            </button>
          </div>

          {/* Tabs - Only show when not collapsed */}
          {!isRightPanelCollapsed && (
            <div className="border-b border-[#64748B]/20 px-6 py-3">
              <div className="flex space-x-6">
                {['Sources', 'Progress'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab as 'Sources' | 'Progress')}
                    className={`text-sm font-medium pb-2 border-b-2 transition-colors ${
                      tab === activeTab
                        ? 'text-[#C46A5A] border-[#C46A5A]' 
                        : 'text-[#475569] dark:text-[#64748B] border-transparent hover:text-[#111827] dark:hover:text-white'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Tab Content - Only show when not collapsed */}
          {!isRightPanelCollapsed && (
            <div className="flex-1 overflow-y-auto p-6">
            {false && (
              <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-[#111827] dark:text-white">
                  Live Draft {multiAgentResearchId && <span className="text-[#3FA796]">(Multi-Agent)</span>}
                </h3>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-[#475569] dark:text-[#64748B]">Show reasoning</span>
                  <input type="checkbox" className="rounded" aria-label="Show reasoning trail" />
                </div>
              </div>
              
              {/* Multi-Agent Status */}
              {multiAgentStatus && (
                <div className="bg-gradient-to-r from-[#3FA796]/10 to-[#2E8B73]/10 p-4 rounded-lg border border-[#3FA796]/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-[#111827] dark:text-white">Multi-Agent Research Status</span>
                    <span className="text-sm text-[#3FA796]">{multiAgentStatus.progress?.toFixed(1)}%</span>
                  </div>
                  <div className="text-sm text-[#475569] dark:text-[#64748B]">
                    {multiAgentStatus.completed_tasks}/{multiAgentStatus.total_tasks} sections completed
                    {multiAgentStatus.agents_active > 0 && (
                      <span className="ml-2">• {multiAgentStatus.agents_active} agents active</span>
                    )}
                  </div>
                </div>
              )}
              
              <div className="space-y-4">
                <div className="border-l-4 border-[#C46A5A] pl-4">
                  <h4 className="font-semibold text-[#111827] dark:text-white">Executive Summary</h4>
                  <div className="text-sm text-[#475569] dark:text-[#64748B] mt-2">
                    {multiAgentOutput?.final_output ? (
                      <div className="max-h-96 overflow-y-auto">
                        <div dangerouslySetInnerHTML={{ __html: multiAgentOutput.final_output.replace(/\n/g, '<br>') }} />
                      </div>
                    ) : researchContent?.executive_summary ? (
                      <div dangerouslySetInnerHTML={{ __html: researchContent.executive_summary.replace(/\n/g, '<br>') }} />
                    ) : multiAgentStatus ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#3FA796]"></div>
                        <span>Multi-agent system generating comprehensive research...</span>
                      </div>
                    ) : researchProgress ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#3FA796]"></div>
                        <span>Generating executive summary...</span>
                      </div>
                    ) : (
                      <p className="text-[#64748B] dark:text-[#64748B]">Start a deep research to see the executive summary here.</p>
                    )}
                  </div>
                  {researchContent?.sources && researchContent.sources.length > 0 && (
                    <div className="flex items-center space-x-2 mt-2">
                      {researchContent.sources.slice(0, 3).map((source: any, index: number) => (
                        <span key={index} className="text-xs bg-[#3FA796]/10 text-[#3FA796] px-2 py-1 rounded">
                          [{index + 1}]
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="border-l-4 border-[#64748B]/30 pl-4">
                  <h4 className="font-semibold text-[#111827] dark:text-white">Legal Framework Analysis</h4>
                  <div className="text-sm text-[#475569] dark:text-[#64748B] mt-2">
                    {researchContent?.legal_framework_analysis ? (
                      <div className="max-h-96 overflow-y-auto">
                        <div dangerouslySetInnerHTML={{ __html: researchContent.legal_framework_analysis.replace(/\n/g, '<br>') }} />
                      </div>
                    ) : researchProgress ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#3FA796]"></div>
                        <span>Generating legal framework analysis...</span>
                      </div>
                    ) : (
                      <p className="text-[#64748B] dark:text-[#64748B]">Start a deep research to see the legal framework analysis here.</p>
                    )}
                  </div>
                </div>
                
                <div className="border-l-4 border-[#64748B]/30 pl-4">
                  <h4 className="font-semibold text-[#111827] dark:text-white">Case Law Synthesis</h4>
                  <div className="text-sm text-[#475569] dark:text-[#64748B] mt-2">
                    {researchContent?.case_law_synthesis ? (
                      <div className="max-h-96 overflow-y-auto">
                        <div dangerouslySetInnerHTML={{ __html: researchContent.case_law_synthesis.replace(/\n/g, '<br>') }} />
                      </div>
                    ) : researchProgress ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#3FA796]"></div>
                        <span>Generating case law synthesis...</span>
                      </div>
                    ) : (
                      <p className="text-[#64748B] dark:text-[#64748B]">Start a deep research to see the case law synthesis here.</p>
                    )}
                  </div>
                </div>
                
                {researchContent?.sources && researchContent.sources.length > 0 && (
                  <div className="border-l-4 border-[#3FA796] pl-4">
                    <h4 className="font-semibold text-[#111827] dark:text-white">Sources Discovered ({researchContent.sources.length})</h4>
                    <div className="text-sm text-[#475569] dark:text-[#64748B] mt-2">
                      <div className="max-h-64 overflow-y-auto space-y-2">
                        {researchContent.sources.slice(0, 10).map((source: any, index: number) => (
                          <div key={index} className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                            <div className="font-medium text-[#111827] dark:text-white">{source.title}</div>
                            <div className="text-[#64748B] dark:text-[#64748B]">
                              {source.kind} • {source.court || 'Source'} • Trust: {(source.trust_score * 100).toFixed(0)}%
                            </div>
                            {source.url && (
                              <a href={source.url} target="_blank" rel="noopener noreferrer" 
                                 className="text-[#3FA796] hover:underline">
                                View Source →
                              </a>
                            )}
                          </div>
                        ))}
                        {researchContent.sources.length > 10 && (
                          <div className="text-center text-[#64748B] dark:text-[#64748B]">
                            ... and {researchContent.sources.length - 10} more sources
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
            )}

            {activeTab === 'Sources' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-[#111827] dark:text-white">Sources Discovered</h3>
                {researchContent?.sources && researchContent.sources.length > 0 ? (
                  <div className="space-y-3">
                    <div className="text-sm text-[#475569] dark:text-[#64748B]">
                      Found {researchContent.sources.length} sources
                    </div>
                    <div className="max-h-96 overflow-y-auto space-y-2">
                      {researchContent.sources.map((source: any, index: number) => (
                        <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                          <div className="font-medium text-[#111827] dark:text-white text-sm">
                            {source.title}
                          </div>
                          <div className="text-xs text-[#64748B] dark:text-[#64748B] mt-1">
                            {source.kind} • {source.court || 'Source'} • Trust: {(source.trust_score * 100).toFixed(0)}%
                          </div>
                          {source.url && (
                            <a href={source.url} target="_blank" rel="noopener noreferrer"
                               className="text-[#3FA796] hover:underline text-xs mt-1 inline-block">
                              View Source →
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-[#475569] dark:text-[#64748B]">
                      {researchProgress ? 'Sources are being discovered...' : 'No sources found yet. Start a deep research to discover sources.'}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'Progress' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-[#111827] dark:text-white">Research Progress</h3>
                {researchProgress ? (
                  <div className="space-y-4">
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-[#111827] dark:text-white">
                          Current Phase: {researchProgress.current_phase}
                        </span>
                        <span className="text-sm text-[#3FA796]">
                          {researchProgress.overall_progress}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-[#3FA796] h-2 rounded-full transition-all duration-300"
                          style={{ width: `${researchProgress.overall_progress}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-[#475569] dark:text-[#64748B] mt-2">
                        {researchProgress.current_activity}
                      </div>
                      <div className="text-xs text-[#64748B] dark:text-[#64748B] mt-1">
                        Elapsed: {researchProgress.elapsed_time}
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-[#111827] dark:text-white">Phase Details</h4>
                      {researchProgress.phases && Object.entries(researchProgress.phases).map(([phase, details]: [string, any]) => (
                        <div key={phase} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          <span className="text-sm text-[#111827] dark:text-white">{phase}</span>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-[#475569] dark:text-[#64748B]">
                              {details.progress}%
                            </span>
                            <div className={`w-2 h-2 rounded-full ${
                              details.status === 'completed' ? 'bg-[#3FA796]' :
                              details.status === 'in_progress' ? 'bg-[#D97706]' :
                              'bg-[#64748B]/30'
                            }`}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-[#475569] dark:text-[#64748B]">
                      No research in progress. Start a deep research to see progress details.
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          )}
        </div>
      </div>

      {/* Scope Wizard Modal */}
      {showDeepResearchForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-[#111827] rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-[#111827] dark:text-white">
                Scope Your Research
              </h3>
              <button
                onClick={() => setShowDeepResearchForm(false)}
                className="text-[#475569] dark:text-[#64748B] hover:text-[#111827] dark:hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left: Form */}
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-[#111827] dark:text-white mb-2">
                    Research Topic *
                  </label>
                  <input
                    type="text"
                    value={researchRequest.topic}
                    onChange={(e) => setResearchRequest(prev => ({ ...prev, topic: e.target.value }))}
                    placeholder="e.g., Data Protection Laws in India"
                    className="w-full px-4 py-3 border border-[#64748B]/30 rounded-xl focus:ring-2 focus:ring-[#C46A5A] focus:border-[#C46A5A] bg-white dark:bg-[#111827] text-[#111827] dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#111827] dark:text-white mb-2">
                    Jurisdictions
                  </label>
                  <input
                    type="text"
                    value={researchRequest.jurisdictions.join(', ')}
                    onChange={(e) => setResearchRequest(prev => ({
                      ...prev,
                      jurisdictions: e.target.value.split(',').map(j => j.trim()).filter(j => j)
                    }))}
                    placeholder="India, UK, US"
                    className="w-full px-4 py-3 border border-[#64748B]/30 rounded-xl focus:ring-2 focus:ring-[#C46A5A] focus:border-[#C46A5A] bg-white dark:bg-[#111827] text-[#111827] dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#111827] dark:text-white mb-2">
                    Research Depth
                  </label>
                                            <select
                                                value={researchRequest.depth_level}
                                                onChange={(e) => setResearchRequest(prev => ({
                                                    ...prev,
                                                    depth_level: e.target.value as 'quick' | 'comprehensive' | 'exhaustive'
                                                }))}
                                                className="w-full px-4 py-3 border border-[#64748B]/30 rounded-xl focus:ring-2 focus:ring-[#C46A5A] focus:border-[#C46A5A] bg-white dark:bg-[#111827] text-[#111827] dark:text-white"
                                                aria-label="Research depth level"
                                            >
                    <option value="quick">Quick (15-30 min)</option>
                    <option value="comprehensive">Comprehensive (45-90 min)</option>
                    <option value="exhaustive">Exhaustive (2-4 hours)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#111827] dark:text-white mb-2">
                    Target Audience
                  </label>
                                            <select
                                                value={researchRequest.audience}
                                                onChange={(e) => setResearchRequest(prev => ({
                                                    ...prev,
                                                    audience: e.target.value as 'legal_professional' | 'student' | 'general'
                                                }))}
                                                className="w-full px-4 py-3 border border-[#64748B]/30 rounded-xl focus:ring-2 focus:ring-[#C46A5A] focus:border-[#C46A5A] bg-white dark:bg-[#111827] text-[#111827] dark:text-white"
                                                aria-label="Target audience"
                                            >
                    <option value="legal_professional">Legal Professional</option>
                    <option value="student">Student</option>
                    <option value="general">General Public</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#111827] dark:text-white mb-2">
                    Research Length (Words)
                  </label>
                  <div className="space-y-3">
                    <input
                      type="range"
                      min="2000"
                      max="50000"
                      step="1000"
                      value={researchRequest.word_count || 50000}
                      onChange={(e) => setResearchRequest(prev => ({ ...prev, word_count: parseInt(e.target.value) }))}
                      className="w-full h-2 bg-[#64748B]/20 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-sm text-[#475569] dark:text-[#64748B]">
                      <span>2K words</span>
                      <span className="font-semibold text-[#3FA796]">{((researchRequest.word_count || 50000) / 1000).toFixed(0)}K words</span>
                      <span>50K words</span>
                    </div>
                    <div className="text-xs text-[#475569] dark:text-[#64748B]">
                      {researchRequest.word_count && researchRequest.word_count <= 10000 && "Quick overview"}
                      {researchRequest.word_count && researchRequest.word_count > 10000 && researchRequest.word_count <= 25000 && "Comprehensive analysis"}
                      {researchRequest.word_count && researchRequest.word_count > 25000 && "Exhaustive research"}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right: Live Outline Preview */}
              <div className="bg-[#F8F7F4] dark:bg-[#0F172A] rounded-xl p-6">
                <h4 className="font-semibold text-[#111827] dark:text-white mb-4">Research Outline Preview</h4>
                <div className="space-y-3 text-sm">
                  <div className="font-medium text-[#111827] dark:text-white">1. Executive Summary</div>
                  <div className="font-medium text-[#111827] dark:text-white">2. Legal Framework Analysis</div>
                  <div className="font-medium text-[#111827] dark:text-white">3. Case Law Synthesis</div>
                  <div className="font-medium text-[#111827] dark:text-white">4. Practical Implementation</div>
                  <div className="font-medium text-[#111827] dark:text-white">5. Risk Assessment</div>
                  <div className="font-medium text-[#111827] dark:text-white">6. Appendices</div>
                </div>
                <div className="mt-4 text-xs text-[#475569] dark:text-[#64748B]">
                  Estimated: {researchRequest.depth_level === 'quick' ? '15-30 pages' : 
                  researchRequest.depth_level === 'comprehensive' ? '50-75 pages' : '75-100+ pages'}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-4 mt-8">
              <button
                onClick={() => setShowDeepResearchForm(false)}
                className="px-6 py-3 border border-[#64748B]/30 text-[#111827] dark:text-white rounded-xl hover:bg-[#F3F4F6] dark:hover:bg-[#1F2937] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={startDeepResearch}
                disabled={!researchRequest.topic.trim() || isLoading}
                className="bg-[#C46A5A] hover:bg-[#B85A4A] text-white px-8 py-3 rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Starting...' : 'Approve Plan & Start'}
              </button>
            </div>
          </div>
        </div>
      )}
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

// AI Message Bubble with Deep Research Types
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
  const getBubbleType = (message: any) => {
    // Check if message.answer exists and has text property
    if (!message.answer || !message.answer.text) {
      return 'generic'
    }
    
    const text = message.answer.text
    if (text.includes('## Research Plan') || text.includes('## Outline')) return 'plan'
    if (text.includes('Starting') && text.includes('Discovery')) return 'status'
    if (text.includes('§') && text.includes('Drafted')) return 'section_draft'
    if (text.includes('Flagged') || text.includes('missing')) return 'qa_flag'
    if (text.includes('Compiled') && text.includes('pages')) return 'export_ready'
    return 'generic'
  }

  const bubbleType = getBubbleType(message)

  const getBubbleIcon = (type: string) => {
    switch (type) {
      case 'plan': return ''
      case 'status': return ''
      case 'section_draft': return ''
      case 'qa_flag': return '⚠️'
      case 'export_ready': return ''
      default: return '⚖️'
    }
  }

  const getBubbleColor = (type: string) => {
    switch (type) {
      case 'plan': return 'bg-[#3FA796]'
      case 'status': return 'bg-[#D97706]'
      case 'section_draft': return 'bg-[#C46A5A]'
      case 'qa_flag': return 'bg-[#EF4444]'
      case 'export_ready': return 'bg-[#3FA796]'
      default: return 'bg-[#C46A5A]'
    }
  }

  return (
    <div className="bg-white dark:bg-[#111827] border border-[#64748B]/20 rounded-xl p-4">
      <div className="flex items-start space-x-3">
        <div className={`w-8 h-8 ${getBubbleColor(bubbleType)} rounded-full flex items-center justify-center text-white text-sm font-bold`}>
          {getBubbleIcon(bubbleType)}
        </div>
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-medium text-[#111827] dark:text-white">
              {bubbleType === 'plan' ? 'Research Planner' :
               bubbleType === 'status' ? 'Research Engine' :
               bubbleType === 'section_draft' ? 'Report Writer' :
               bubbleType === 'qa_flag' ? 'Quality Assurance' :
               bubbleType === 'export_ready' ? 'Export Manager' :
               'JurisBrain AI'}
            </span>
            <span className="text-xs text-[#475569] dark:text-[#64748B]">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
          
          <div className="prose prose-sm max-w-none text-[#111827] dark:text-white">
            <div className="whitespace-pre-wrap">
              {(message.answer?.text || '').split('\n').map((line, index) => {
                // Handle bold text formatting
                if (line.includes('**') && line.includes(':**')) {
                  const parts = line.split('**')
                  return (
                    <div key={index} className="mb-2">
                      <strong className="text-[#C46A5A]">{parts[1]}</strong>
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

          {/* Action Chips for Deep Research */}
          {bubbleType === 'plan' && (
            <div className="mt-4 flex space-x-2">
              <button className="px-4 py-2 bg-[#3FA796] hover:bg-[#2E8B73] text-white text-sm rounded-lg font-medium transition-colors">
                Approve Plan
              </button>
              <button className="px-4 py-2 border border-[#64748B]/30 text-[#111827] dark:text-white text-sm rounded-lg font-medium hover:bg-[#F3F4F6] dark:hover:bg-[#1F2937] transition-colors">
                Edit Scope
              </button>
            </div>
          )}

          {bubbleType === 'section_draft' && (
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="px-3 py-1 bg-[#3FA796]/10 text-[#3FA796] text-xs rounded-full hover:bg-[#3FA796]/20 transition-colors">
                Add contrary views
              </button>
              <button className="px-3 py-1 bg-[#3FA796]/10 text-[#3FA796] text-xs rounded-full hover:bg-[#3FA796]/20 transition-colors">
                Extend to EU/US
              </button>
              <button className="px-3 py-1 bg-[#3FA796]/10 text-[#3FA796] text-xs rounded-full hover:bg-[#3FA796]/20 transition-colors">
                Export draft §4.2
              </button>
            </div>
          )}

          {bubbleType === 'qa_flag' && (
            <div className="mt-4 flex space-x-2">
              <button className="px-4 py-2 bg-[#EF4444] hover:bg-[#DC2626] text-white text-sm rounded-lg font-medium transition-colors">
                Add Missing View
              </button>
              <button className="px-4 py-2 border border-[#64748B]/30 text-[#111827] dark:text-white text-sm rounded-lg font-medium hover:bg-[#F3F4F6] dark:hover:bg-[#1F2937] transition-colors">
                Skip
              </button>
            </div>
          )}

          {bubbleType === 'export_ready' && (
            <div className="mt-4 flex space-x-2">
              <button className="px-4 py-2 bg-[#3FA796] hover:bg-[#2E8B73] text-white text-sm rounded-lg font-medium transition-colors">
                Download DOCX
              </button>
              <button className="px-4 py-2 bg-[#3FA796] hover:bg-[#2E8B73] text-white text-sm rounded-lg font-medium transition-colors">
                Download PDF
              </button>
              <button className="px-4 py-2 border border-[#64748B]/30 text-[#111827] dark:text-white text-sm rounded-lg font-medium hover:bg-[#F3F4F6] dark:hover:bg-[#1F2937] transition-colors">
                Research Pack
              </button>
            </div>
          )}

          {/* Citations */}
          {message.citations && message.citations.length > 0 && (
            <div className="mt-4">
              <div className="text-xs text-[#475569] dark:text-[#64748B] mb-2">Sources:</div>
              <div className="flex flex-wrap gap-1">
                {(message.citations || []).map((citation) => (
                  <button
                    key={citation.pin}
                    className="px-2 py-1 text-xs bg-[#3FA796]/10 text-[#3FA796] rounded-full hover:bg-[#3FA796]/20 transition-colors"
                    title={`${citation.title} - ${citation.court_or_source}`}
                  >
                    [{citation.pin}]
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Reasoning Trail */}
          {message.reasoning_trail && message.reasoning_trail.length > 0 && (
            <div className="mt-3">
              <button
                onClick={onToggleReasoning}
                className="text-xs text-[#C46A5A] hover:underline"
              >
                {showReasoning ? 'Hide' : 'Show'} reasoning
              </button>
              {showReasoning && (
                <div className="mt-2 p-3 bg-[#F8F7F4] dark:bg-[#0F172A] rounded-lg">
                  <div className="text-xs text-[#475569] dark:text-[#64748B]">
                    <strong>Research Process:</strong>
                  </div>
                  <div className="text-xs text-[#475569] dark:text-[#64748B] mt-1">
                    {message.reasoning_trail.map((step, index) => (
                      <div key={index} className="mb-1">
                        <strong>{step.step}:</strong> {step.notes}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Follow-up Questions */}
          {message.followups && message.followups.length > 0 && (
            <div className="mt-4">
              <div className="text-xs text-[#475569] dark:text-[#64748B] mb-2">
                Follow-up questions:
              </div>
              <div className="flex flex-wrap gap-2">
                {message.followups.map((followup, index) => (
                  <button
                    key={index}
                    onClick={() => onFollowUpClick(followup)}
                    className="px-3 py-1 bg-[#C46A5A]/10 text-[#C46A5A] text-xs rounded-full hover:bg-[#C46A5A]/20 transition-colors"
                  >
                    {followup}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// AI Loading Bubble
function AILoadingBubble() {
  return (
    <div className="bg-white dark:bg-[#111827] border border-[#64748B]/20 rounded-xl p-4">
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 bg-[#D97706] rounded-full flex items-center justify-center">
          <span className="text-white font-bold text-sm"></span>
        </div>
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-medium text-[#111827] dark:text-white">Research Engine</span>
            <span className="text-xs text-[#475569] dark:text-[#64748B]">working...</span>
          </div>
          <div className="flex items-center space-x-1 mb-2">
            <div className="w-2 h-2 bg-[#D97706] rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-[#D97706] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-[#D97706] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <div className="text-xs text-[#475569] dark:text-[#64748B]">
            Planning your research and discovering sources...
          </div>
        </div>
      </div>
    </div>
  )
}