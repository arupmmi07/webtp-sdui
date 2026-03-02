import { Avatar, Box, Stack, Typography } from '@mui/material'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import { IconButton } from '@/components/wrappers/IconButton'
import { useActionExecutor } from '@/renderer/ActionContext'

export interface MessageAction {
  icon?: string
  onClick?: () => void
  action?: Record<string, unknown>
  disabled?: boolean
  [key: string]: unknown
}

interface MessageProps {
  avatar?: string
  timestamp?: string
  content?: string
  header?: React.ReactNode
  highlight?: string
  actions?: MessageAction[]
  children?: React.ReactNode
  [key: string]: unknown
}

export function Message({
  avatar,
  timestamp,
  content,
  header,
  highlight,
  actions = [],
  children,
  bubbleSx,
  contentSx,
  headerSx,
  childrenPosition = 'after',
  ...rest
}: MessageProps) {
  const execute = useActionExecutor()
  const displayContent = content ?? (typeof children === 'string' ? children : null)

  const getActionHandler = (item: MessageAction) => {
    if (item.onClick) return item.onClick
    if (item.action && typeof item.action === 'object') {
      return () => execute(item.action as Record<string, unknown>)
    }
    return undefined
  }

  return (
    <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start', maxWidth: 720 }} {...rest}>
      <Avatar
        src={typeof avatar === 'string' && avatar.startsWith('http') ? avatar : undefined}
        sx={{ width: 36, height: 36, flexShrink: 0, bgcolor: 'grey.300' }}
      >
        {typeof avatar === 'string' && !avatar.startsWith('http') ? (
          avatar.slice(0, 2).toUpperCase()
        ) : (
          <SmartToyIcon sx={{ fontSize: 20 }} />
        )}
      </Avatar>
      <Stack direction="column" spacing={0.5} flex={1} minWidth={0}>
        {timestamp && (
          <Typography variant="caption" color="text.secondary">
            {timestamp}
          </Typography>
        )}
        <Box
          sx={{
            bgcolor: 'grey.100',
            borderRadius: 2,
            px: 2,
            py: 1.5,
            border: '1px solid',
            borderColor: 'divider',
            ...(bubbleSx as object),
          }}
        >
          {header && (
            <Typography variant="body2" component="div" sx={{ color: 'grey.600', mb: 1, ...(headerSx as object) }}>
              {header}
            </Typography>
          )}
          {(displayContent || (typeof children === 'string' ? children : null) || highlight) && (
            <Typography variant="body2" component="div" sx={{ whiteSpace: 'pre-wrap', ...(contentSx as object) }}>
              {(displayContent ?? (typeof children === 'string' ? children : null)) as React.ReactNode}
              {highlight && (
                <>
                  {displayContent || (typeof children === 'string' ? children : null) ? ' ' : null}
                  <Typography component="span" variant="body2" sx={{ color: 'error.main', fontWeight: 500 }}>
                    {highlight}
                  </Typography>
                </>
              )}
            </Typography>
          )}
          {children && typeof children !== 'string' && childrenPosition === 'before' && (
            <Stack spacing={1} sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              {children}
            </Stack>
          )}
          {actions.length > 0 && (
            <Stack direction="row" spacing={0.5} sx={{ mt: 1 }}>
              {actions.map((action, idx) => {
                const defaultSx = {
                  border: '1px solid',
                  borderColor: '#6633FF',
                  backgroundColor: 'white',
                  color: '#6633FF',
                  '&:hover': { backgroundColor: 'grey.50' },
                  '&.Mui-disabled': { backgroundColor: 'white', color: '#6633FF', opacity: 0.6 },
                }
                const actionSx = (action.sx as object) ?? {}
                return (
                  <IconButton
                    key={idx}
                    icon={action.icon as string}
                    onClick={getActionHandler(action)}
                    disabled={action.disabled}
                    sx={{ ...defaultSx, ...actionSx }}
                  />
                )
              })}
            </Stack>
          )}
          {children && typeof children !== 'string' && childrenPosition === 'after' && (
            <Stack
              spacing={1}
              sx={
                displayContent || actions.length > 0
                  ? { mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }
                  : { mt: 0 }
              }
            >
              {children}
            </Stack>
          )}
        </Box>
      </Stack>
    </Box>
  )
}
