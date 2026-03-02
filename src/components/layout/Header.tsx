import { AppBar, Toolbar, TextField, InputAdornment, IconButton, Avatar, Box, Badge } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import FilterListIcon from '@mui/icons-material/FilterList'
import GridViewIcon from '@mui/icons-material/GridView'
import NotificationsIcon from '@mui/icons-material/Notifications'
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'

function WebptLogo() {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2 }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 0.5,
          height: 24,
        }}
      >
        <Box sx={{ width: 4, height: 16, bgcolor: '#6B46C1', borderRadius: 0.5 }} />
        <Box sx={{ width: 4, height: 12, bgcolor: '#E53E3E', borderRadius: 0.5 }} />
        <Box sx={{ width: 4, height: 20, bgcolor: '#3182CE', borderRadius: 0.5 }} />
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'baseline' }}>
        <Box component="span" sx={{ fontSize: '1.125rem', fontWeight: 500, color: 'text.primary' }}>
          web
        </Box>
        <Box component="span" sx={{ fontSize: '0.95rem', fontWeight: 700, color: 'text.primary', ml: 0.25 }}>
          pt
        </Box>
      </Box>
    </Box>
  )
}

export function Header() {
  return (
    <AppBar position="sticky" color="default" elevation={0} sx={{ borderBottom: 1, borderColor: 'grey.300', bgcolor: '#fff' }}>
      <Toolbar sx={{ gap: 1.5, minHeight: 64 }}>
        <WebptLogo />
        <TextField
          size="small"
          placeholder="Search patients, providers, referrals, authorizations, and appointments..."
          variant="outlined"
          sx={{
            flex: 1,
            maxWidth: 520,
            '& .MuiOutlinedInput-root': {
              bgcolor: '#fff',
              borderRadius: 2,
              borderColor: 'grey.300',
              '& fieldset': { borderColor: 'grey.300' },
              '&:hover fieldset': { borderColor: 'grey.400' },
            },
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end" sx={{ mr: 0.5 }}>
                <SearchIcon sx={{ fontSize: 20, color: 'grey.500' }} />
              </InputAdornment>
            ),
          }}
        />
        <IconButton
          size="small"
          sx={{
            border: '1px solid',
            borderColor: 'primary.main',
            color: 'primary.main',
            borderRadius: '50%',
            width: 36,
            height: 36,
            '&:hover': { bgcolor: 'primary.light', color: 'primary.contrastText', borderColor: 'primary.main' },
          }}
        >
          <FilterListIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" sx={{ color: 'primary.main' }}>
          <GridViewIcon />
        </IconButton>
        <IconButton size="small" sx={{ color: 'primary.main', position: 'relative' }}>
          <Badge badgeContent={2} color="error" sx={{ '& .MuiBadge-badge': { fontSize: 10, minWidth: 16, height: 16 } }}>
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <IconButton size="small" sx={{ color: 'primary.main' }}>
          <ChatBubbleOutlineIcon />
        </IconButton>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1, cursor: 'pointer' }}>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              bgcolor: 'grey.400',
            }}
          >
            JD
          </Avatar>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', fontSize: '0.875rem', fontWeight: 500, color: 'text.primary' }}>
              John Doe
              <KeyboardArrowDownIcon sx={{ fontSize: 18, ml: 0.25, color: 'primary.main' }} />
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', fontSize: '0.75rem', color: 'text.secondary' }}>
              Santa Clara Street
              <KeyboardArrowDownIcon sx={{ fontSize: 16, ml: 0.25, color: 'primary.main' }} />
            </Box>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  )
}
