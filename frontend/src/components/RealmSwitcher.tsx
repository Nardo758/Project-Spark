import { useState } from 'react'
import { MapPin, Globe, ChevronDown } from 'lucide-react'

type Realm = 'physical' | 'digital'

interface RealmSwitcherProps {
  currentRealm: Realm
  onRealmChange: (realm: Realm) => void
  disabled?: boolean
}

export default function RealmSwitcher({
  currentRealm,
  onRealmChange,
  disabled = false
}: RealmSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false)

  const realms = [
    {
      id: 'physical' as Realm,
      name: 'Physical Realm',
      description: 'Location-based opportunities',
      icon: MapPin,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20'
    },
    {
      id: 'digital' as Realm,
      name: 'Digital Realm',
      description: 'Online business opportunities',
      icon: Globe,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/20'
    }
  ]

  const currentRealmData = realms.find((r) => r.id === currentRealm) || realms[0]
  const CurrentIcon = currentRealmData.icon

  return (
    <div className="relative">
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`flex items-center gap-3 px-4 py-2 rounded-lg border transition-all ${
          disabled
            ? 'opacity-50 cursor-not-allowed border-gray-700 bg-gray-800'
            : 'border-gray-600 bg-gray-800 hover:border-gray-500 cursor-pointer'
        }`}
      >
        <div className={`p-1.5 rounded ${currentRealmData.bgColor}`}>
          <CurrentIcon className={`w-4 h-4 ${currentRealmData.color}`} />
        </div>
        <div className="text-left">
          <div className="text-sm font-medium text-white">{currentRealmData.name}</div>
          <div className="text-xs text-gray-400">{currentRealmData.description}</div>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && !disabled && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full left-0 mt-2 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20">
            {realms.map((realm) => {
              const Icon = realm.icon
              const isSelected = realm.id === currentRealm

              return (
                <button
                  key={realm.id}
                  onClick={() => {
                    onRealmChange(realm.id)
                    setIsOpen(false)
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 transition-colors first:rounded-t-lg last:rounded-b-lg ${
                    isSelected
                      ? 'bg-gray-700'
                      : 'hover:bg-gray-700/50'
                  }`}
                >
                  <div className={`p-1.5 rounded ${realm.bgColor}`}>
                    <Icon className={`w-4 h-4 ${realm.color}`} />
                  </div>
                  <div className="text-left flex-1">
                    <div className="text-sm font-medium text-white">{realm.name}</div>
                    <div className="text-xs text-gray-400">{realm.description}</div>
                  </div>
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-purple-500" />
                  )}
                </button>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
