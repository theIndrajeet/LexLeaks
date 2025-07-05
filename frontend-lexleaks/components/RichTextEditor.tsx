'use client'

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import Highlight from '@tiptap/extension-highlight'
import { Color } from '@tiptap/extension-color'
import TextStyle from '@tiptap/extension-text-style'
import FontFamily from '@tiptap/extension-font-family'
import Underline from '@tiptap/extension-underline'
import CodeBlock from '@tiptap/extension-code-block'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import Superscript from '@tiptap/extension-superscript'
import Subscript from '@tiptap/extension-subscript'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import HorizontalRule from '@tiptap/extension-horizontal-rule'
import Youtube from '@tiptap/extension-youtube'
import CharacterCount from '@tiptap/extension-character-count'
import { useCallback, useState, useEffect } from 'react'

interface RichTextEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
  className?: string
}

const MenuBar = ({ editor, isHtmlMode, setIsHtmlMode }: { editor: any, isHtmlMode: boolean, setIsHtmlMode: (value: boolean) => void }) => {
  const [showFontMenu, setShowFontMenu] = useState(false)
  const [showColorMenu, setShowColorMenu] = useState(false)
  const [showInsertMenu, setShowInsertMenu] = useState(false)
  const [showTableMenu, setShowTableMenu] = useState(false)

  if (!editor) {
    return null
  }

  const setLink = useCallback(() => {
    const previousUrl = editor.getAttributes('link').href
    const url = window.prompt('URL', previousUrl)

    if (url === null) {
      return
    }

    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run()
      return
    }

    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
  }, [editor])

  const addImage = useCallback(() => {
    const url = window.prompt('Image URL')
    if (url) {
      editor.chain().focus().setImage({ src: url }).run()
    }
  }, [editor])

  const addYoutubeVideo = useCallback(() => {
    const url = window.prompt('YouTube URL')
    if (url) {
      editor.chain().focus().setYoutubeVideo({ src: url }).run()
    }
  }, [editor])

  const pasteAsPlainText = useCallback(async () => {
    try {
      const text = await navigator.clipboard.readText()
      if (text) {
        // Split text into paragraphs
        const paragraphs = text.split(/\n\n+/)
        const html = paragraphs
          .filter(p => p.trim())
          .map(p => `<p>${p.trim()}</p>`)
          .join('')
        
        if (html) {
          editor.chain().focus().insertContent(html).run()
        }
      }
    } catch (err) {
      // Fallback for browsers that don't support clipboard API
      const text = window.prompt('Paste your text here:')
      if (text) {
        const paragraphs = text.split(/\n\n+/)
        const html = paragraphs
          .filter(p => p.trim())
          .map(p => `<p>${p.trim()}</p>`)
          .join('')
        
        if (html) {
          editor.chain().focus().insertContent(html).run()
        }
      }
    }
  }, [editor])

  const colors = [
    '#000000', '#434343', '#666666', '#999999', '#B7B7B7', '#CCCCCC', '#D9D9D9', '#EFEFEF', '#F3F3F3', '#FFFFFF',
    '#980000', '#FF0000', '#FF9900', '#FFFF00', '#00FF00', '#00FFFF', '#4A86E8', '#0000FF', '#9900FF', '#FF00FF',
    '#8B0000', '#FF6B6B', '#FFA500', '#FFD700', '#32CD32', '#40E0D0', '#4169E1', '#8A2BE2', '#DA70D6', '#FF1493'
  ]

  const fonts = [
    { name: 'Default', value: 'Inter' },
    { name: 'Arial', value: 'Arial' },
    { name: 'Georgia', value: 'Georgia' },
    { name: 'Impact', value: 'Impact' },
    { name: 'Courier New', value: 'Courier New' },
    { name: 'Times New Roman', value: 'Times New Roman' },
    { name: 'Verdana', value: 'Verdana' },
    { name: 'Comic Sans MS', value: 'Comic Sans MS' }
  ]

  return (
    <div className="border-b-2 brand-border bg-[#f5f0d8] dark:bg-[#2a251f]">
      {/* First toolbar row */}
      <div className="flex flex-wrap items-center gap-1 px-4 py-2 border-b brand-border">
        {/* HTML Mode Toggle */}
        <button
          type="button"
          onClick={() => setIsHtmlMode(!isHtmlMode)}
          className={`px-3 py-1.5 rounded-sm transition-colors text-sm font-mono-special ${
            isHtmlMode 
              ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
              : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
          }`}
          title={isHtmlMode ? "Switch to Visual Mode" : "Switch to HTML Mode"}
        >
          {isHtmlMode ? 'Visual' : 'HTML'}
        </button>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Undo/Redo */}
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().chain().focus().undo().run() || isHtmlMode}
            className="p-2 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] disabled:opacity-50"
            title="Undo (Cmd+Z)"
          >
            ↶
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().chain().focus().redo().run() || isHtmlMode}
            className="p-2 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] disabled:opacity-50"
            title="Redo (Cmd+Shift+Z)"
          >
            ↷
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Font Family Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowFontMenu(!showFontMenu)}
            disabled={isHtmlMode}
            className="px-3 py-1.5 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm font-mono-special flex items-center gap-1 disabled:opacity-50"
          >
            {editor.getAttributes('textStyle').fontFamily || 'Font'}
            <span className="text-xs">▼</span>
          </button>
          {showFontMenu && !isHtmlMode && (
            <div className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 border-2 brand-border rounded-sm shadow-lg z-50 min-w-[150px]">
              {fonts.map((font) => (
                <button
                  key={font.value}
                  type="button"
                  onClick={() => {
                    editor.chain().focus().setFontFamily(font.value).run()
                    setShowFontMenu(false)
                  }}
                  className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
                  style={{ fontFamily: font.value }}
                >
                  {font.name}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Heading Dropdown */}
        <select
          onChange={(e) => {
            const level = parseInt(e.target.value)
            if (level === 0) {
              editor.chain().focus().setParagraph().run()
            } else {
              editor.chain().focus().toggleHeading({ level: level as any }).run()
            }
          }}
          value={
            editor.isActive('heading', { level: 1 }) ? 1 :
            editor.isActive('heading', { level: 2 }) ? 2 :
            editor.isActive('heading', { level: 3 }) ? 3 :
            editor.isActive('heading', { level: 4 }) ? 4 :
            editor.isActive('heading', { level: 5 }) ? 5 :
            editor.isActive('heading', { level: 6 }) ? 6 : 0
          }
          className="px-3 py-1.5 rounded-sm bg-[#fdf6e3] dark:bg-[#1a1612] border brand-border text-sm font-mono-special"
        >
          <option value="0">Normal</option>
          <option value="1">Heading 1</option>
          <option value="2">Heading 2</option>
          <option value="3">Heading 3</option>
          <option value="4">Heading 4</option>
          <option value="5">Heading 5</option>
          <option value="6">Heading 6</option>
        </select>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Text Style Buttons */}
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive('bold') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Bold (Cmd+B)"
          >
            <strong>B</strong>
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive('italic') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Italic (Cmd+I)"
          >
            <em>I</em>
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleUnderline().run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive('underline') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Underline (Cmd+U)"
          >
            <u>U</u>
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleStrike().run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive('strike') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Strikethrough"
          >
            <s>S</s>
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleCode().run()}
            className={`p-2 rounded-sm transition-colors text-sm font-mono ${
              editor.isActive('code') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Inline Code"
          >
            {'</>'}
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleSuperscript().run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive('superscript') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Superscript"
          >
            X²
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleSubscript().run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive('subscript') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Subscript"
          >
            X₂
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Color Options */}
        <div className="flex gap-1">
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowColorMenu(!showColorMenu)}
              className="px-3 py-1.5 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm flex items-center gap-1"
              title="Text Color"
            >
              <span style={{ color: editor.getAttributes('textStyle').color || '#000' }}>A</span>
              <span className="text-xs">▼</span>
            </button>
            {showColorMenu && (
              <div className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 border-2 brand-border rounded-sm shadow-lg z-50 p-2">
                <div className="grid grid-cols-10 gap-1">
                  {colors.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => {
                        editor.chain().focus().setColor(color).run()
                        setShowColorMenu(false)
                      }}
                      className="w-6 h-6 rounded border border-gray-300 hover:scale-110 transition-transform"
                      style={{ backgroundColor: color }}
                      title={color}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleHighlight().run()}
            className={`px-3 py-1.5 rounded-sm transition-colors text-sm ${
              editor.isActive('highlight') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Highlight"
          >
            🖍️
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Insert Menu */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowInsertMenu(!showInsertMenu)}
            className="px-3 py-1.5 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm font-mono-special flex items-center gap-1"
          >
            Insert <span className="text-xs">▼</span>
          </button>
          {showInsertMenu && (
            <div className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 border-2 brand-border rounded-sm shadow-lg z-50 min-w-[150px]">
              <button
                type="button"
                onClick={() => {
                  setLink()
                  setShowInsertMenu(false)
                }}
                className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
              >
                🔗 Link
              </button>
              <button
                type="button"
                onClick={() => {
                  addImage()
                  setShowInsertMenu(false)
                }}
                className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
              >
                🖼️ Image
              </button>
              <button
                type="button"
                onClick={() => {
                  addYoutubeVideo()
                  setShowInsertMenu(false)
                }}
                className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
              >
                📹 YouTube Video
              </button>
              <button
                type="button"
                onClick={() => {
                  editor.chain().focus().setHorizontalRule().run()
                  setShowInsertMenu(false)
                }}
                className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
              >
                — Horizontal Line
              </button>
              <button
                type="button"
                onClick={() => {
                  editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
                  setShowInsertMenu(false)
                }}
                className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
              >
                📊 Table
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Second toolbar row */}
      <div className="flex flex-wrap items-center gap-1 px-4 py-2">
        {/* Alignment */}
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => editor.chain().focus().setTextAlign('left').run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive({ textAlign: 'left' }) 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Align Left"
          >
            ⬅
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().setTextAlign('center').run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive({ textAlign: 'center' }) 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Align Center"
          >
            ⬌
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().setTextAlign('right').run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive({ textAlign: 'right' }) 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Align Right"
          >
            ➡
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().setTextAlign('justify').run()}
            className={`p-2 rounded-sm transition-colors text-sm ${
              editor.isActive({ textAlign: 'justify' }) 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Justify"
          >
            ☰
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Lists */}
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={`px-3 py-1.5 rounded-sm transition-colors text-sm font-mono-special ${
              editor.isActive('bulletList') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Bullet List"
          >
            • List
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={`px-3 py-1.5 rounded-sm transition-colors text-sm font-mono-special ${
              editor.isActive('orderedList') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Numbered List"
          >
            1. List
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleTaskList().run()}
            className={`px-3 py-1.5 rounded-sm transition-colors text-sm font-mono-special ${
              editor.isActive('taskList') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Task List"
          >
            ☐ Tasks
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Indentation */}
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => editor.chain().focus().outdent().run()}
            className="p-2 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
            title="Decrease Indent"
          >
            ⇤
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().indent().run()}
            className="p-2 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
            title="Increase Indent"
          >
            ⇥
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Blocks */}
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            className={`px-3 py-1.5 rounded-sm transition-colors text-sm font-mono-special ${
              editor.isActive('blockquote') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Quote"
          >
            " Quote
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            className={`px-3 py-1.5 rounded-sm transition-colors text-sm font-mono-special ${
              editor.isActive('codeBlock') 
                ? 'bg-[#8B0000] dark:bg-[#d4766f] text-white dark:text-gray-900' 
                : 'hover:bg-[#eee8d5] dark:hover:bg-[#3a352f]'
            }`}
            title="Code Block"
          >
            {'</>'}
          </button>
        </div>

        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

        {/* Table controls (shown when in a table) */}
        {editor.isActive('table') && (
          <>
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowTableMenu(!showTableMenu)}
                className="px-3 py-1.5 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm font-mono-special flex items-center gap-1"
              >
                Table <span className="text-xs">▼</span>
              </button>
              {showTableMenu && (
                <div className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 border-2 brand-border rounded-sm shadow-lg z-50 min-w-[150px]">
                  <button
                    type="button"
                    onClick={() => {
                      editor.chain().focus().addColumnBefore().run()
                      setShowTableMenu(false)
                    }}
                    className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
                  >
                    Insert Column Before
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      editor.chain().focus().addColumnAfter().run()
                      setShowTableMenu(false)
                    }}
                    className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
                  >
                    Insert Column After
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      editor.chain().focus().deleteColumn().run()
                      setShowTableMenu(false)
                    }}
                    className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm text-red-600"
                  >
                    Delete Column
                  </button>
                  <hr className="my-1 border-gray-300 dark:border-gray-600" />
                  <button
                    type="button"
                    onClick={() => {
                      editor.chain().focus().addRowBefore().run()
                      setShowTableMenu(false)
                    }}
                    className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
                  >
                    Insert Row Before
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      editor.chain().focus().addRowAfter().run()
                      setShowTableMenu(false)
                    }}
                    className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm"
                  >
                    Insert Row After
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      editor.chain().focus().deleteRow().run()
                      setShowTableMenu(false)
                    }}
                    className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm text-red-600"
                  >
                    Delete Row
                  </button>
                  <hr className="my-1 border-gray-300 dark:border-gray-600" />
                  <button
                    type="button"
                    onClick={() => {
                      editor.chain().focus().deleteTable().run()
                      setShowTableMenu(false)
                    }}
                    className="block w-full text-left px-3 py-2 hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm text-red-600"
                  >
                    Delete Table
                  </button>
                </div>
              )}
            </div>
            <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />
          </>
        )}

        {/* Clear Formatting */}
        <button
          type="button"
          onClick={() => editor.chain().focus().unsetAllMarks().clearNodes().run()}
          className="px-3 py-1.5 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm font-mono-special"
          title="Clear Formatting"
        >
          Clear Format
        </button>

        {/* Paste as Plain Text */}
        <button
          type="button"
          onClick={pasteAsPlainText}
          className="px-3 py-1.5 rounded-sm transition-colors hover:bg-[#eee8d5] dark:hover:bg-[#3a352f] text-sm font-mono-special"
          title="Paste as Plain Text"
        >
          📋 Plain Text
        </button>

        {/* Character count */}
        <div className="ml-auto text-sm text-gray-600 dark:text-gray-400 font-mono-special">
          {editor.storage.characterCount.characters()} chars | {editor.storage.characterCount.words()} words
        </div>
      </div>
    </div>
  )
}

export default function RichTextEditor({
  content,
  onChange,
  placeholder = 'Start writing...',
  className = ''
}: RichTextEditorProps) {
  const [isHtmlMode, setIsHtmlMode] = useState(false)
  const [htmlContent, setHtmlContent] = useState(content || '')

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6]
        }
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-[#8B0000] dark:text-[#d4766f] underline hover:opacity-80'
        }
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full h-auto rounded-lg my-4'
        }
      }),
      Placeholder.configure({
        placeholder
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph']
      }),
      Highlight.configure({
        multicolor: true
      }),
      TextStyle,
      Color,
      FontFamily,
      Underline,
      CodeBlock.configure({
        HTMLAttributes: {
          class: 'bg-gray-100 dark:bg-gray-900 rounded-md p-4 my-4 font-mono text-sm'
        }
      }),
      Table.configure({
        resizable: true,
        HTMLAttributes: {
          class: 'border-collapse table-auto w-full my-4'
        }
      }),
      TableRow.configure({
        HTMLAttributes: {
          class: 'border border-gray-300 dark:border-gray-600'
        }
      }),
      TableHeader.configure({
        HTMLAttributes: {
          class: 'border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 font-bold p-2'
        }
      }),
      TableCell.configure({
        HTMLAttributes: {
          class: 'border border-gray-300 dark:border-gray-600 p-2'
        }
      }),
      Superscript,
      Subscript,
      TaskList.configure({
        HTMLAttributes: {
          class: 'not-prose pl-2'
        }
      }),
      TaskItem.configure({
        nested: true,
        HTMLAttributes: {
          class: 'flex items-start'
        }
      }),
      HorizontalRule,
      Youtube.configure({
        width: 640,
        height: 480,
        HTMLAttributes: {
          class: 'rounded-lg my-4'
        }
      }),
      CharacterCount
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      const html = editor.getHTML()
      setHtmlContent(html)
      onChange(html)
    },
    editorProps: {
      attributes: {
        class: 'prose prose-base dark:prose-invert max-w-none focus:outline-none min-h-[400px] px-4 py-3 [&_*]:max-w-none'
      },
      handlePaste: (view, event) => {
        const clipboardData = event.clipboardData
        if (!clipboardData) return false
        
        const html = clipboardData.getData('text/html')
        const text = clipboardData.getData('text/plain')
        
        // If there's HTML content from any source
        if (html) {
          event.preventDefault()
          
          // Create a temporary div to parse the HTML
          const tempDiv = document.createElement('div')
          tempDiv.innerHTML = html
          
          // Remove all style attributes first
          tempDiv.querySelectorAll('*').forEach(el => {
            el.removeAttribute('style')
            el.removeAttribute('class')
            el.removeAttribute('id')
          })
          
          // Keep only allowed tags
          const allowedTags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 
                              'strong', 'b', 'em', 'i', 'u', 'strike', 's', 'br', 'a', 
                              'blockquote', 'code', 'pre', 'table', 'thead', 'tbody', 
                              'tr', 'th', 'td', 'img', 'hr', 'sup', 'sub']
          
          // Function to clean an element
          const cleanElement = (el: Element) => {
            // Remove all attributes except href for links and src/alt for images
            const tagName = el.tagName.toLowerCase()
            const attrs = Array.from(el.attributes)
            
            attrs.forEach(attr => {
              if (tagName === 'a' && attr.name === 'href') {
                return // Keep href
              } else if (tagName === 'img' && (attr.name === 'src' || attr.name === 'alt')) {
                return // Keep src and alt
              } else {
                el.removeAttribute(attr.name)
              }
            })
            
            // Clean child elements
            Array.from(el.children).forEach(child => cleanElement(child))
          }
          
          // Process all elements
          const allElements = Array.from(tempDiv.querySelectorAll('*'))
          
          allElements.forEach(el => {
            const tagName = el.tagName.toLowerCase()
            
            // Replace disallowed tags with their content
            if (!allowedTags.includes(tagName)) {
              // For divs and spans, replace with paragraph if they contain text
              if ((tagName === 'div' || tagName === 'span') && el.textContent?.trim()) {
                const p = document.createElement('p')
                p.innerHTML = el.innerHTML
                el.replaceWith(p)
              } else {
                // For other tags, just unwrap the content
                el.replaceWith(...Array.from(el.childNodes))
              }
            } else {
              // Clean allowed elements
              cleanElement(el)
            }
          })
          
          // Convert bold/strong tags that might be causing issues
          tempDiv.querySelectorAll('b').forEach(el => {
            const strong = document.createElement('strong')
            strong.innerHTML = el.innerHTML
            el.replaceWith(strong)
          })
          
          // Final cleanup
          let cleanHtml = tempDiv.innerHTML
            // Remove empty paragraphs
            .replace(/<p[^>]*>[\s&nbsp;]*<\/p>/gi, '')
            // Remove excessive line breaks
            .replace(/(<br\s*\/?>[\s]*){3,}/gi, '<br><br>')
            // Clean up whitespace
            .replace(/&nbsp;/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
          
          // If we still have content, insert it
          if (cleanHtml && editor) {
            // For very simple content (just text), insert as paragraph
            if (!cleanHtml.includes('<')) {
              cleanHtml = `<p>${cleanHtml}</p>`
            }
            
            editor.chain().focus().insertContent(cleanHtml).run()
            return true
          }
        } else if (text) {
          // For plain text, prevent default and insert as paragraphs
          event.preventDefault()
          
          // Split text into paragraphs
          const paragraphs = text.split(/\n\n+/)
          const html = paragraphs
            .filter(p => p.trim())
            .map(p => `<p>${p.trim()}</p>`)
            .join('')
          
          if (html && editor) {
            editor.chain().focus().insertContent(html).run()
            return true
          }
        }
        
        // Let TipTap handle other cases
        return false
      }
    }
  })

  // Sync editor content when switching from HTML to visual mode
  useEffect(() => {
    if (!isHtmlMode && editor && htmlContent !== editor.getHTML()) {
      editor.commands.setContent(htmlContent)
    }
  }, [isHtmlMode])

  // Update HTML content when content prop changes
  useEffect(() => {
    if (content !== htmlContent) {
      setHtmlContent(content || '')
      if (editor && !isHtmlMode) {
        editor.commands.setContent(content || '')
      }
    }
  }, [content])

  const handleHtmlChange = (value: string) => {
    setHtmlContent(value)
    onChange(value)
  }

  if (!editor) {
    return null
  }

  return (
    <div className={`border-2 brand-border rounded-sm bg-[#fdf6e3] dark:bg-[#1a1612] ${className}`}>
      <MenuBar editor={editor} isHtmlMode={isHtmlMode} setIsHtmlMode={setIsHtmlMode} />
      
      {isHtmlMode ? (
        <div className="relative">
          <textarea
            value={htmlContent}
            onChange={(e) => handleHtmlChange(e.target.value)}
            className="w-full min-h-[400px] px-4 py-3 bg-[#fdf6e3] dark:bg-[#1a1612] text-gray-900 dark:text-gray-100 font-mono text-sm resize-y focus:outline-none"
            placeholder="Paste or write your HTML here..."
          />
          <div className="absolute top-2 right-2 text-xs text-gray-500 dark:text-gray-400 font-mono-special">
            HTML Mode
          </div>
        </div>
      ) : (
        <EditorContent editor={editor} />
      )}
      
      {/* Status bar */}
      <div className="border-t-2 brand-border px-4 py-2 bg-[#f5f0d8] dark:bg-[#2a251f] text-xs text-gray-600 dark:text-gray-400 font-mono-special">
        {isHtmlMode 
          ? 'HTML Mode: Paste or edit raw HTML directly' 
          : 'Press Cmd+K for links • Drag & drop images • YouTube URLs auto-embed'
        }
      </div>
    </div>
  )
} 