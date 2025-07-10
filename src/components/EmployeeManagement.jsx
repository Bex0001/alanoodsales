import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useAuth } from '@/contexts/AuthContext'
import { PlusCircle, Edit, Trash2, User } from 'lucide-react'

function EmployeeManagement() {
  const { token, user } = useAuth()
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const API_BASE = 'https://9yhyi3cz0k7q.manus.space/api'

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await fetch(`${API_BASE}/admin/employees`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (!response.ok) {
          throw new Error('فشل في جلب بيانات الموظفين')
        }
        const data = await response.json()
        setEmployees(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    if (user && (user.role === 'admin' || user.role === 'sales_manager' || user.role === 'team_leader')) {
      fetchEmployees()
    } else {
      setError('ليس لديك صلاحية لعرض هذه الصفحة.')
      setLoading(false)
    }
  }, [token, user])

  if (loading) return <div className="text-center py-8">جاري تحميل بيانات الموظفين...</div>
  if (error) return <div className="text-center py-8 text-red-500">خطأ: {error}</div>

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">إدارة الموظفين</h1>

      <Card className="apple-card">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>قائمة الموظفين</CardTitle>
          {(user.role === 'admin' || user.role === 'sales_manager') && (
            <Button className="apple-button">
              <PlusCircle className="ml-2 h-4 w-4" /> إضافة موظف جديد
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>الاسم</TableHead>
                <TableHead>البريد الإلكتروني</TableHead>
                <TableHead>الدور</TableHead>
                <TableHead>الراتب الأساسي</TableHead>
                <TableHead>الفريق</TableHead>
                <TableHead>تاريخ التعيين</TableHead>
                <TableHead>الحالة</TableHead>
                {(user.role === 'admin' || user.role === 'sales_manager') && (
                  <TableHead className="text-center">الإجراءات</TableHead>
                )}
              </TableRow>
            </TableHeader>
            <TableBody>
              {employees.map((employee) => (
                <TableRow key={employee.id}>
                  <TableCell className="font-medium flex items-center">
                    <User className="h-4 w-4 ml-2 text-muted-foreground" /> {employee.name}
                  </TableCell>
                  <TableCell>{employee.email}</TableCell>
                  <TableCell>{employee.role}</TableCell>
                  <TableCell>{employee.base_salary?.toLocaleString()} ريال</TableCell>
                  <TableCell>{employee.team_name || 'لا يوجد'}</TableCell>
                  <TableCell>{employee.hire_date || 'غير محدد'}</TableCell>
                  <TableCell>{employee.is_active ? 'نشط' : 'غير نشط'}</TableCell>
                  {(user.role === 'admin' || user.role === 'sales_manager') && (
                    <TableCell className="text-center">
                      <Button variant="ghost" size="sm" className="ml-2">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="text-red-500">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

export default EmployeeManagement


