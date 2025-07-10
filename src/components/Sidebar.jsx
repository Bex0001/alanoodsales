import { Link } from 'react-router-dom'
import { Home, Users, Briefcase, BarChart2, Settings, ChevronLeft, ChevronRight, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'

function Sidebar({ isOpen, onToggle, user }) {
  const { isDark, toggleTheme } = useTheme()
  const { logout } = useAuth()

  const navItems = [
    { name: 'لوحة التحكم', icon: Home, path: '/dashboard', roles: ['admin', 'sales_manager', 'team_leader', 'sales_rep'] },
    { name: 'إدارة الموظفين', icon: Users, path: '/employees', roles: ['admin', 'sales_manager', 'team_leader'] },
    { name: 'إدارة المشاريع', icon: Briefcase, path: '/projects', roles: ['admin', 'sales_manager', 'team_leader', 'sales_rep'] },
    { name: 'التقارير', icon: BarChart2, path: '/reports', roles: ['admin', 'sales_manager', 'team_leader'] },
    { name: 'لوحة الإدارة', icon: Settings, path: '/admin', roles: ['admin', 'sales_manager'] },
  ]

  return (
    <div
      className={`relative h-full flex flex-col transition-all duration-300 ease-in-out
        ${isOpen ? 'w-64' : 'w-20'} 
        ${isDark ? 'bg-gray-900 text-gray-100' : 'bg-white text-gray-900'}
        border-l ${isDark ? 'border-gray-700' : 'border-gray-200'}
      `}
      dir="rtl"
    >
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        {isOpen && <h1 className="text-2xl font-bold text-blue-600">العنود للمبيعات</h1>}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={`rounded-full ${isOpen ? 'ml-auto' : 'mx-auto'}`}
        >
          {isOpen ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
        </Button>
      </div>

      <nav className="flex-1 px-2 py-4 space-y-1">
        {navItems.map((item) => (
          user && item.roles.includes(user.role) && (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center rounded-md p-3 text-sm font-medium
                ${isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-100'}
                ${isOpen ? 'justify-start' : 'justify-center'}
              `}
            >
              <item.icon className={`h-5 w-5 ${isOpen ? 'ml-3' : ''}`} />
              {isOpen && item.name}
            </Link>
          )
        ))}
      </nav>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="ghost"
          className={`w-full flex items-center justify-center
            ${isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-100'}
          `}
          onClick={toggleTheme}
        >
          {isOpen && (isDark ? 'الوضع الفاتح' : 'الوضع الداكن')}
          <span className={`${isOpen ? 'ml-2' : ''}`}>
            {isDark ? '☀️' : '🌙'}
          </span>
        </Button>
        <Button
          variant="ghost"
          className={`w-full flex items-center justify-center mt-2
            ${isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-100'}
          `}
          onClick={logout}
        >
          <LogOut className={`h-5 w-5 ${isOpen ? 'ml-3' : ''}`} />
          {isOpen && 'تسجيل الخروج'}
        </Button>
      </div>
    </div>
  )
}

export default Sidebar


