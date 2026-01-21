import { useState, useCallback, useEffect, memo } from 'react'
import { Excalidraw, MainMenu, WelcomeScreen } from '@excalidraw/excalidraw'

interface ExcalidrawCanvasProps {
  opportunityId?: string
  onSave?: (elements: readonly any[]) => void
}

function ExcalidrawCanvas({ onSave }: ExcalidrawCanvasProps) {
  const [, setExcalidrawAPI] = useState<any>(null)
  const [elements, setElements] = useState<readonly any[]>([])

  const handleChange = useCallback((
    newElements: readonly any[],
    _appState: any
  ) => {
    setElements(newElements)
  }, [])

  const handleSave = useCallback(() => {
    if (onSave && elements.length > 0) {
      onSave(elements)
    }
  }, [elements, onSave])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        handleSave()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleSave])

  return (
    <div className="h-full w-full" style={{ height: '100%' }}>
      <Excalidraw
        excalidrawAPI={(api: any) => setExcalidrawAPI(api)}
        onChange={handleChange}
        theme="dark"
        UIOptions={{
          canvasActions: {
            saveToActiveFile: false,
            loadScene: true,
            export: { saveFileToDisk: true },
            clearCanvas: true,
          },
        }}
      >
        <MainMenu>
          <MainMenu.DefaultItems.LoadScene />
          <MainMenu.DefaultItems.Export />
          <MainMenu.DefaultItems.SaveAsImage />
          <MainMenu.DefaultItems.ClearCanvas />
          <MainMenu.DefaultItems.ToggleTheme />
          <MainMenu.DefaultItems.ChangeCanvasBackground />
        </MainMenu>
        <WelcomeScreen>
          <WelcomeScreen.Center>
            <WelcomeScreen.Center.Heading>
              Digital Workspace
            </WelcomeScreen.Center.Heading>
            <WelcomeScreen.Center.Menu>
              <WelcomeScreen.Center.MenuItemLink href="https://excalidraw.com">
                Start Drawing
              </WelcomeScreen.Center.MenuItemLink>
            </WelcomeScreen.Center.Menu>
          </WelcomeScreen.Center>
        </WelcomeScreen>
      </Excalidraw>
    </div>
  )
}

export default memo(ExcalidrawCanvas)
