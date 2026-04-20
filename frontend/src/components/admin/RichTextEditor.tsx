"use client";

import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import {
  Bold,
  Italic,
  List,
  ListOrdered,
  Quote,
  Redo2,
  Undo2,
} from "lucide-react";
import { type MouseEvent, useEffect } from "react";

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export function RichTextEditor({ value, onChange }: RichTextEditorProps) {
  const headingLevels = [1, 2, 3, 4, 5, 6] as const;

  const editorStyles =
    "w-full min-h-[180px] outline-none p-4 text-slate-900 " +
    "[&_p]:mb-3 [&_p]:leading-7 " +
    "[&_h1]:mb-3 [&_h1]:mt-6 [&_h1]:text-3xl [&_h1]:font-bold [&_h1]:leading-tight " +
    "[&_h2]:mb-3 [&_h2]:mt-5 [&_h2]:text-2xl [&_h2]:font-semibold [&_h2]:leading-tight " +
    "[&_h3]:mb-2 [&_h3]:mt-5 [&_h3]:text-xl [&_h3]:font-semibold [&_h3]:leading-snug " +
    "[&_h4]:mb-2 [&_h4]:mt-4 [&_h4]:text-lg [&_h4]:font-semibold [&_h4]:leading-snug " +
    "[&_h5]:mb-2 [&_h5]:mt-4 [&_h5]:text-base [&_h5]:font-semibold " +
    "[&_h6]:mb-2 [&_h6]:mt-4 [&_h6]:text-sm [&_h6]:font-semibold [&_h6]:uppercase [&_h6]:tracking-[0.12em] " +
    "[&_blockquote]:my-4 [&_blockquote]:border-l-4 [&_blockquote]:border-slate-300 [&_blockquote]:pl-4 [&_blockquote]:text-slate-600 " +
    "[&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-6 " +
    "[&_li]:mb-1 [&_hr]:my-5 [&_hr]:border-slate-200 [&_.ProseMirror-trailingBreak]:select-none";

  const editor = useEditor({
    extensions: [StarterKit],
    content: value,
    immediatelyRender: false,
    editorProps: {
      attributes: {
        class: editorStyles,
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  useEffect(() => {
    if (!editor) return;

    const currentHtml = editor.getHTML();
    if (currentHtml !== value) {
      editor.commands.setContent(value, { emitUpdate: false });
    }
  }, [editor, value]);

  if (!editor) {
    return null;
  }

  const keepFocus = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  const headingButtonClass = (level: 1 | 2 | 3 | 4 | 5 | 6) => {
    const active = editor.isActive("heading", { level });
    return `rounded-md px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-slate-100 ${
      active
        ? "bg-slate-900 text-white"
        : "border border-slate-200 text-slate-700"
    }`;
  };

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-wrap items-center gap-3 border-b border-slate-200 bg-white px-4 py-3">
        <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5 shadow-sm">
          <button
            type="button"
            className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-slate-100 ${
              editor.isActive("paragraph")
                ? "bg-slate-900 text-white"
                : "border border-slate-200 text-slate-700"
            }`}
            onMouseDown={keepFocus}
            onClick={() => editor.chain().setParagraph().run()}
            aria-label="Paragraph"
            title="Paragraph"
          >
            P
          </button>

          {headingLevels.map((level) => (
            <button
              key={level}
              type="button"
              className={headingButtonClass(level)}
              onMouseDown={keepFocus}
              onClick={() => editor.chain().toggleHeading({ level }).run()}
              aria-label={`Heading ${level}`}
              title={`Heading ${level}`}
            >
              H{level}
            </button>
          ))}

          <button
            type="button"
            className={`inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-slate-100 ${
              editor.isActive("blockquote")
                ? "bg-slate-900 text-white"
                : "border border-slate-200 text-slate-700"
            }`}
            onMouseDown={keepFocus}
            onClick={() => editor.chain().toggleBlockquote().run()}
            aria-label="Blockquote"
            title="Blockquote"
          >
            <Quote className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5 shadow-sm">
          <button
            type="button"
            className={`inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-slate-100 ${
              editor.isActive("bold")
                ? "bg-slate-900 text-white"
                : "border border-slate-200 text-slate-700"
            }`}
            onMouseDown={keepFocus}
            onClick={() => editor.chain().toggleBold().run()}
            aria-label="Bold"
            title="Bold"
          >
            <Bold className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            className={`inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-slate-100 ${
              editor.isActive("italic")
                ? "bg-slate-900 text-white"
                : "border border-slate-200 text-slate-700"
            }`}
            onMouseDown={keepFocus}
            onClick={() => editor.chain().toggleItalic().run()}
            aria-label="Italic"
            title="Italic"
          >
            <Italic className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5 shadow-sm">
          <button
            type="button"
            className={`inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-slate-100 ${
              editor.isActive("bulletList")
                ? "bg-slate-900 text-white"
                : "border border-slate-200 text-slate-700"
            }`}
            onMouseDown={keepFocus}
            onClick={() => editor.chain().toggleBulletList().run()}
            aria-label="Bullet list"
            title="Bullet list"
          >
            <List className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            className={`inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-slate-100 ${
              editor.isActive("orderedList")
                ? "bg-slate-900 text-white"
                : "border border-slate-200 text-slate-700"
            }`}
            onMouseDown={keepFocus}
            onClick={() => editor.chain().toggleOrderedList().run()}
            aria-label="Numbered list"
            title="Numbered list"
          >
            <ListOrdered className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5 shadow-sm">
          <button
            type="button"
            className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
            onMouseDown={keepFocus}
            onClick={() => editor.chain().undo().run()}
            aria-label="Undo"
            title="Undo"
          >
            <Undo2 className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
            onMouseDown={keepFocus}
            onClick={() => editor.chain().redo().run()}
            aria-label="Redo"
            title="Redo"
          >
            <Redo2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <div
        className="cursor-text border-r border-slate-200 last:border-r-0 bg-white"
        onClick={() => editor.chain().focus().run()}
      >
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}
