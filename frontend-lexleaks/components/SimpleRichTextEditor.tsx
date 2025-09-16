'use client'

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import { Color } from '@tiptap/extension-color'
import TextStyle from '@tiptap/extension-text-style'
import Underline from '@tiptap/extension-underline'
import { useCallback, useState, useEffect } from 'react'

interface SimpleRichTextEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
  className?: string
  rows?: number
}

const SimpleMenuBar = ({ editor, isHtmlMode, setIsHtmlMode }: any) => {
  const [htmlContent, setHtmlContent] = useState('')

  const handleHtmlChange = useCallback((value: string) => {
    setHtmlContent(value)
    if (editor) {
      editor.commands.setContent(value)
    }
  }, [editor])

  useEffect(() => {
    if (isHtmlMode && editor) {
      setHtmlContent(editor.getHTML())
    }
  }, [isHtmlMode, editor])

  if (!editor) {
    return null
  }

  return (
    <div className="border-b-2 brand-border bg-[#f5f0d8] dark:bg-[#2a251f] p-2">
      <div className="flex flex-wrap items-center gap-1">
        {/* HTML Toggle */}
        <button
          onClick={() => setIsHtmlMode(!isHtmlMode)}
          className={`px-2 py-1 text-xs font-mono-special rounded ${
            isHtmlMode 
              ? 'bg-[#8B0000] text-white' 
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
          title="Toggle HTML Mode"
        >
          HTML
        </button>

        {!isHtmlMode && (
          <>
            {/* Basic Formatting */}
            <button
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={`px-2 py-1 text-xs font-mono-special rounded ${
                editor.isActive('bold') 
                  ? 'bg-[#8B0000] text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Bold"
            >
              B
            </button>
            <button
              onClick={() => editor.chain().focus().toggleItalic().run()}
              className={`px-2 py-1 text-xs font-mono-special rounded ${
                editor.isActive('italic') 
                  ? 'bg-[#8B0000] text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Italic"
            >
              I
            </button>
            <button
              onClick={() => editor.chain().focus().toggleUnderline().run()}
              className={`px-2 py-1 text-xs font-mono-special rounded ${
                editor.isActive('underline') 
                  ? 'bg-[#8B0000] text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Underline"
            >
              U
            </button>

            {/* Separator */}
            <div className="w-px h-4 bg-gray-400 dark:bg-gray-600 mx-1"></div>

            {/* Lists */}
            <button
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              className={`px-2 py-1 text-xs font-mono-special rounded ${
                editor.isActive('bulletList') 
                  ? 'bg-[#8B0000] text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Bullet List"
            >
              •
            </button>
            <button
              onClick={() => editor.chain().focus().toggleOrderedList().run()}
              className={`px-2 py-1 text-xs font-mono-special rounded ${
                editor.isActive('orderedList') 
                  ? 'bg-[#8B0000] text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Numbered List"
            >
              1.
            </button>

            {/* Separator */}
            <div className="w-px h-4 bg-gray-400 dark:bg-gray-600 mx-1"></div>

            {/* Links */}
            <button
              onClick={() => {
                const url = window.prompt('Enter URL:')
                if (url) {
                  editor.chain().focus().setLink({ href: url }).run()
                }
              }}
              className={`px-2 py-1 text-xs font-mono-special rounded ${
                editor.isActive('link') 
                  ? 'bg-[#8B0000] text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Add Link"
            >
              🔗
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default function SimpleRichTextEditor({
  content,
  onChange,
  placeholder = 'Start writing...',
  className = '',
  rows = 3
}: SimpleRichTextEditorProps) {
  
  const [htmlContent, setHtmlContent] = useState(content || '')
  const [isHtmlMode, setIsHtmlMode] = useState(false)

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3]
        }
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-[#8B0000] dark:text-[#d4766f] underline hover:opacity-80'
        }
      }),
      Placeholder.configure({
        placeholder
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph']
      }),
      TextStyle,
      Color,
      Underline
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      const html = editor.getHTML()
      onChange(html)
    },
    editorProps: {
      attributes: {
        class: `prose prose-sm max-w-none min-h-[${rows * 1.5}rem] px-4 py-3 bg-[#fdf6e3] dark:bg-[#1a1612] text-gray-900 dark:text-gray-100 focus:outline-none`,
      },
    },
  })

  const handleHtmlChange = useCallback((value: string) => {
    setHtmlContent(value)
    onChange(value)
  }, [onChange])

  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content || '')
    }
  }, [content, editor])

  if (!editor) {
    return null
  }

  return (
    <div className={`border-2 brand-border rounded-sm bg-[#fdf6e3] dark:bg-[#1a1612] ${className}`}>
      <SimpleMenuBar editor={editor} isHtmlMode={isHtmlMode} setIsHtmlMode={setIsHtmlMode} />
      
      {isHtmlMode ? (
        <div className="relative">
          <textarea
            value={htmlContent}
            onChange={(e) => handleHtmlChange(e.target.value)}
            className="w-full min-h-[120px] px-4 py-3 bg-[#fdf6e3] dark:bg-[#1a1612] text-gray-900 dark:text-gray-100 font-mono text-sm resize-y focus:outline-none"
            placeholder="Paste or write your HTML here..."
            rows={rows}
          />
          <div className="absolute top-2 right-2 text-xs text-gray-500 dark:text-gray-400 font-mono-special">
            HTML Mode
          </div>
        </div>
      ) : (
        <EditorContent editor={editor} />
      )}
      
      {/* Status bar */}
      <div className="border-t-2 brand-border px-4 py-1 bg-[#f5f0d8] dark:bg-[#2a251f] text-xs text-gray-600 dark:text-gray-400 font-mono-special">
        {isHtmlMode 
          ? 'HTML Mode: Paste or edit raw HTML directly' 
          : 'Press Cmd+K for links • Basic formatting available'
        }
      </div>
    </div>
  )
}
