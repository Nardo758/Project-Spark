import { useState } from 'react'
import {
  ChevronDown, ChevronRight, CheckCircle2, Plus,
  Loader2, AlertCircle, Layers
} from 'lucide-react'

interface Props {
  workspaceId: number
  workspace: any
  token: string
  onRefresh: () => void
}

const STATUS_BADGES: Record<string, { label: string; color: string }> = {
  not_started: { label: 'Not Started', color: 'bg-stone-100 text-stone-600' },
  in_progress: { label: 'In Progress', color: 'bg-blue-100 text-blue-700' },
  completed: { label: 'Completed', color: 'bg-emerald-100 text-emerald-700' },
}

export default function WorkflowTab({ workspaceId, workspace, token, onRefresh }: Props) {
  const [expandedStages, setExpandedStages] = useState<Set<number>>(new Set((workspace.stages || []).map((s: any) => s.id)))
  const [addingTask, setAddingTask] = useState<number | null>(null)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [loadingTask, setLoadingTask] = useState<number | null>(null)
  const [creatingTask, setCreatingTask] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const stages = [...(workspace.stages || [])].sort((a: any, b: any) => a.stage_order - b.stage_order)

  const toggleStage = (stageId: number) => {
    const next = new Set(expandedStages)
    if (next.has(stageId)) next.delete(stageId)
    else next.add(stageId)
    setExpandedStages(next)
  }

  const completeTask = async (taskId: number, isCompleted: boolean) => {
    setLoadingTask(taskId)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ is_completed: !isCompleted }),
      })
      if (!res.ok) throw new Error('Failed to update task')
      onRefresh()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoadingTask(null)
    }
  }

  const addTask = async (stageId: number) => {
    if (!newTaskTitle.trim()) return
    setCreatingTask(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ stage_id: stageId, title: newTaskTitle.trim() }),
      })
      if (!res.ok) throw new Error('Failed to add task')
      setNewTaskTitle('')
      setAddingTask(null)
      onRefresh()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setCreatingTask(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-stone-900 flex items-center gap-2">
        <Layers className="w-5 h-5 text-violet-500" />
        Workflow Stages
      </h2>

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {stages.length === 0 ? (
        <div className="text-center py-12 text-stone-500">
          <Layers className="w-12 h-12 mx-auto mb-3 text-stone-300" />
          <p>No workflow stages configured.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {stages.map((stage: any) => {
            const isExpanded = expandedStages.has(stage.id)
            const tasks = [...(stage.tasks || [])].sort((a: any, b: any) => a.sort_order - b.sort_order)
            const completedCount = tasks.filter((t: any) => t.is_completed).length
            const totalCount = tasks.length
            const statusBadge = STATUS_BADGES[stage.status] || STATUS_BADGES.not_started

            return (
              <div key={stage.id} className="bg-white border border-stone-200 rounded-xl overflow-hidden">
                <button
                  onClick={() => toggleStage(stage.id)}
                  className="w-full flex items-center gap-3 p-4 text-left hover:bg-stone-50 transition-colors"
                >
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-stone-400 flex-shrink-0" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-stone-400 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-stone-900">{stage.name}</span>
                      <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${statusBadge.color}`}>
                        {statusBadge.label}
                      </span>
                    </div>
                    {stage.description && (
                      <p className="text-xs text-stone-500 truncate">{stage.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span className="text-xs text-stone-500">{completedCount}/{totalCount}</span>
                    <div className="w-24 h-2 bg-stone-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full transition-all"
                        style={{ width: `${totalCount > 0 ? (completedCount / totalCount) * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                </button>

                {isExpanded && (
                  <div className="border-t border-stone-100 p-4 space-y-2">
                    {tasks.map((task: any) => (
                      <div
                        key={task.id}
                        className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                          task.is_completed
                            ? 'bg-stone-50 border-stone-100'
                            : 'bg-white border-stone-200 hover:border-stone-300'
                        }`}
                      >
                        <button
                          onClick={() => completeTask(task.id, task.is_completed)}
                          disabled={loadingTask === task.id}
                          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                            task.is_completed
                              ? 'bg-emerald-500 border-emerald-500 text-white'
                              : 'border-stone-300 hover:border-violet-400'
                          }`}
                        >
                          {loadingTask === task.id ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : task.is_completed ? (
                            <CheckCircle2 className="w-3 h-3" />
                          ) : null}
                        </button>
                        <div className="flex-1 min-w-0">
                          <span className={`text-sm ${task.is_completed ? 'text-stone-400 line-through' : 'text-stone-900'}`}>
                            {task.title}
                          </span>
                          {task.ai_suggestion && (
                            <p className="text-xs text-violet-500 mt-0.5">💡 {task.ai_suggestion}</p>
                          )}
                        </div>
                      </div>
                    ))}

                    {tasks.length === 0 && (
                      <p className="text-sm text-stone-400 text-center py-2">No tasks in this stage yet.</p>
                    )}

                    {addingTask === stage.id ? (
                      <div className="flex items-center gap-2 mt-2">
                        <input
                          type="text"
                          value={newTaskTitle}
                          onChange={(e) => setNewTaskTitle(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && addTask(stage.id)}
                          placeholder="New task title..."
                          autoFocus
                          className="flex-1 px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
                        />
                        <button
                          onClick={() => addTask(stage.id)}
                          disabled={!newTaskTitle.trim() || creatingTask}
                          className="px-3 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
                        >
                          {creatingTask ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => { setAddingTask(null); setNewTaskTitle('') }}
                          className="px-3 py-2 text-stone-500 hover:text-stone-700 text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => { setAddingTask(stage.id); setNewTaskTitle('') }}
                        className="flex items-center gap-1 text-sm text-violet-600 hover:text-violet-700 mt-1"
                      >
                        <Plus className="w-4 h-4" />
                        Add Task
                      </button>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
