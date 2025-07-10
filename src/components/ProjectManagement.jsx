import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useAuth } from '@/contexts/AuthContext'
import { PlusCircle, Edit, Trash2, Briefcase } from 'lucide-react'

function ProjectManagement() {
  const { token, user } = useAuth()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const API_BASE = 'https://9yhyi3cz0k7q.manus.space/api'

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(`${API_BASE}/admin/projects`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (!response.ok) {
          throw new Error('فشل في جلب بيانات المشاريع')
        }
        const data = await response.json()
        setProjects(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    if (user) {
      fetchProjects()
    } else {
      setError('ليس لديك صلاحية لعرض هذه الصفحة.')
      setLoading(false)
    }
  }, [token, user])

  if (loading) return <div className="text-center py-8">جاري تحميل بيانات المشاريع...</div>
  if (error) return <div className="text-center py-8 text-red-500">خطأ: {error}</div>

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">إدارة المشاريع</h1>

      <Card className="apple-card">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>قائمة المشاريع</CardTitle>
          {(user.role === 'admin' || user.role === 'sales_manager' || user.role === 'sales_rep') && (
            <Button className="apple-button">
              <PlusCircle className="ml-2 h-4 w-4" /> إضافة مشروع جديد
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>اسم العميل</TableHead>
                <TableHead>قيمة المشروع</TableHead>
                <TableHead>نوع المنتج</TableHead>
                <TableHead>تاريخ التوقيع</TableHead>
                <TableHead>من السوشيال ميديا؟</TableHead>
                <TableHead>الموظف</TableHead>
                <TableHead className="text-center">الإجراءات</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell className="font-medium flex items-center">
                    <Briefcase className="h-4 w-4 ml-2 text-muted-foreground" /> {project.client_name}
                  </TableCell>
                  <TableCell>{project.project_value?.toLocaleString()} ريال</TableCell>
                  <TableCell>{project.product_type}</TableCell>
                  <TableCell>{project.signature_date}</TableCell>
                  <TableCell>{project.is_from_social_media ? 'نعم' : 'لا'}</TableCell>
                  <TableCell>{project.employee_name || 'غير محدد'}</TableCell>
                  <TableCell className="text-center">
                    <Button variant="ghost" size="sm" className="ml-2">
                      <Edit className="h-4 w-4" />
                    </Button>
                    {(user.role === 'admin' || user.role === 'sales_manager') && (
                      <Button variant="ghost" size="sm" className="text-red-500">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

export default ProjectManagement


