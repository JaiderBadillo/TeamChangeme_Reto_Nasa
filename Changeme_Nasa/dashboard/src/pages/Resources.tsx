import { useState } from 'react'
import { ArrowUpRight, BookmarkPlus, FolderGit2, Trash2 } from 'lucide-react'
import { FlameTitle } from '../components/FlameTitle'

interface CustomResource {
  id: string
  title: string
  category: string
  url: string
}

export function Resources() {
  const [resources, setResources] = useState<CustomResource[]>([])
  const [title, setTitle] = useState('')
  const [category, setCategory] = useState('API / Endpoint')
  const [url, setUrl] = useState('')

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !url.trim()) return
    setResources((prev) => [
      ...prev,
      {
        id: `${Date.now()}`,
        title: title.trim(),
        category,
        url: url.trim(),
      },
    ])
    setTitle('')
    setUrl('')
  }

  return (
    <div className="space-y-6">
      <FlameTitle>Resources</FlameTitle>

      <section className="svg-black-panel p-6 md:p-10 space-y-8">
        <p className="svg-lead-text max-w-3xl mx-auto text-center">
          Organize project links, documentation URLs, and external backend references dynamically without preloaded files or static analysis blocks.
        </p>

        {/* Add Custom Resource Form */}
        <form onSubmit={handleAdd} className="svg-subpanel p-5 space-y-4">
          <div className="flex items-center gap-2">
            <BookmarkPlus className="w-5 h-5 text-[#FEB352]" />
            <h2 className="svg-section-heading text-lg">Add Reference Link</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Resource title..."
              className="svg-input px-3 py-2 text-sm"
            />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="svg-input px-3 py-2 text-sm"
            >
              <option value="API / Endpoint">API / Endpoint</option>
              <option value="Repository">Repository</option>
              <option value="Documentation">Documentation</option>
            </select>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              className="svg-input px-3 py-2 text-sm font-[var(--font-mono)]"
            />
            <button
              type="submit"
              className="svg-chip-active px-4 py-2 text-xs rounded-full cursor-pointer"
            >
              Save Link
            </button>
          </div>
        </form>

        {/* Saved Resources List */}
        <div className="space-y-4">
          <h2 className="svg-section-heading text-xl">Workspace Links ({resources.length})</h2>

          {resources.length === 0 ? (
            <div className="svg-subpanel p-8 text-center space-y-2">
              <FolderGit2 className="w-7 h-7 text-[#B7E4F9] mx-auto" />
              <p className="text-sm text-[#9B8F83]">
                No links added yet. Add documentation, API endpoints, or repository references above as needed.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {resources.map((item) => (
                <div key={item.id} className="svg-subpanel p-4 flex items-center justify-between gap-3">
                  <div className="min-w-0 space-y-1">
                    <span className="text-[11px] px-2 py-0.5 rounded-full border border-[#B7E4F9]/40 text-[#B7E4F9]">
                      {item.category}
                    </span>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 text-sm font-semibold text-[#F5EDE4] hover:text-[#FEB352] truncate"
                    >
                      <span className="truncate">{item.title}</span>
                      <ArrowUpRight className="w-3.5 h-3.5 shrink-0" />
                    </a>
                    <p className="text-xs font-[var(--font-mono)] text-[#9B8F83] truncate">{item.url}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setResources((prev) => prev.filter((r) => r.id !== item.id))}
                    className="p-1.5 rounded-lg border border-[#F27756]/35 text-[#F27756] hover:bg-[#F27756]/10 cursor-pointer shrink-0"
                    aria-label={`Remove ${item.title}`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
