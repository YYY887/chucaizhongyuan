const THEME_KEY = 'chucai-admin-theme'

export function getTheme() {
  return localStorage.getItem(THEME_KEY) || 'light'
}

export function setTheme(theme) {
  localStorage.setItem(THEME_KEY, theme)
  document.documentElement.classList.toggle('dark', theme === 'dark')
}

export function initTheme() {
  setTheme(getTheme())
}

export function toggleTheme() {
  const nextTheme = getTheme() === 'dark' ? 'light' : 'dark'
  setTheme(nextTheme)
  return nextTheme
}
