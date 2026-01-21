import { memo } from 'react'
import { MapPin, Globe } from 'lucide-react'

type Realm = 'physical' | 'digital'

interface WorkspaceTabsProps {
  currentRealm: Realm
  onRealmChange: (realm: Realm) => void
  disabled?: boolean
}

function WorkspaceTabs({
  currentRealm,
  onRealmChange,
  disabled = false
}: WorkspaceTabsProps) {
  const tabs = [
    {
      id: 'physical' as Realm,
      name: 'Map',
      icon: MapPin,
      color: 'text-blue-400',
      activeColor: 'bg-blue-500/20 border-blue-500'
    },
    {
      id: 'digital' as Realm,
      name: 'Digital',
      icon: Globe,
      color: 'text-purple-400',
      activeColor: 'bg-purple-500/20 border-purple-500'
    }
  ]

  return (
    <div className="flex rounded-lg border border-gray-700 overflow-hidden">
      {tabs.map((tab) => {
        const Icon = tab.icon
        const isActive = currentRealm === tab.id

        return (
          <button
            key={tab.id}
            onClick={() => !disabled && onRealmChange(tab.id)}
            disabled={disabled}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all ${
              disabled
                ? 'opacity-50 cursor-not-allowed'
                : 'cursor-pointer'
            } ${
              isActive
                ? `${tab.activeColor} border-b-2`
                : 'bg-gray-800 hover:bg-gray-700 border-b-2 border-transparent'
            }`}
          >
            <Icon className={`w-4 h-4 ${isActive ? tab.color : 'text-gray-400'}`} />
            <span className={isActive ? 'text-white' : 'text-gray-300'}>
              {tab.name}
            </span>
          </button>
        )
      })}
    </div>
  )
}

export default memo(WorkspaceTabs)
