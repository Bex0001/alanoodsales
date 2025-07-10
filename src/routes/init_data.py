from flask import Blueprint, jsonify
from src.models.user import db
from src.models.sales import (
    Employee, Team, Project, Target, MarketingBudget, 
    PerformanceKPI, PerformanceScore, Commission, CommissionRate
)
from datetime import datetime, date
import random

init_bp = Blueprint('init', __name__)

@init_bp.route('/init-sample-data', methods=['POST'])
def init_sample_data():
    """تهيئة البيانات التجريبية"""
    
    try:
        # حذف البيانات الموجودة
        db.session.query(Commission).delete()
        db.session.query(PerformanceScore).delete()
        db.session.query(PerformanceKPI).delete()
        db.session.query(MarketingBudget).delete()
        db.session.query(Target).delete()
        db.session.query(Project).delete()
        db.session.query(Employee).delete()
        db.session.query(Team).delete()
        
        # إنشاء الفرق
        team1 = Team(name="فريق الحديد والألومنيوم")
        team2 = Team(name="فريق الخشب والديكور")
        
        db.session.add(team1)
        db.session.add(team2)
        db.session.commit()
        
        # إنشاء الموظفين
        # مدير المبيعات
        manager = Employee(
            name="أحمد محمد علي",
            role="sales_manager",
            base_salary=15000,
            phone="0501234567",
            email="ahmed@aloud.com",
            hire_date=date(2020, 1, 15)
        )
        
        # قادة الفرق
        team_leader1 = Employee(
            name="سارة أحمد",
            role="team_leader",
            base_salary=8000,
            team_id=team1.id,
            phone="0509876543",
            email="sara@aloud.com",
            hire_date=date(2021, 3, 10)
        )
        
        team_leader2 = Employee(
            name="نورا سعد",
            role="team_leader",
            base_salary=8000,
            team_id=team2.id,
            phone="0545678901",
            email="nora@aloud.com",
            hire_date=date(2021, 5, 12)
        )
        
        # مناديب المبيعات - الفريق الأول
        sales_rep1 = Employee(
            name="محمد عبدالله",
            role="sales_rep",
            base_salary=5000,
            team_id=team1.id,
            phone="0512345678",
            email="mohammed@aloud.com",
            hire_date=date(2021, 6, 20)
        )
        
        sales_rep2 = Employee(
            name="فاطمة حسن",
            role="sales_rep",
            base_salary=5000,
            team_id=team1.id,
            phone="0523456789",
            email="fatima@aloud.com",
            hire_date=date(2021, 8, 15)
        )
        
        sales_rep3 = Employee(
            name="عبدالرحمن خالد",
            role="sales_rep",
            base_salary=5000,
            team_id=team1.id,
            phone="0534567890",
            email="abdulrahman@aloud.com",
            hire_date=date(2022, 1, 10)
        )
        
        # مناديب المبيعات - الفريق الثاني
        sales_rep4 = Employee(
            name="خالد عمر",
            role="sales_rep",
            base_salary=5000,
            team_id=team2.id,
            phone="0556789012",
            email="khalid@aloud.com",
            hire_date=date(2021, 9, 8)
        )
        
        sales_rep5 = Employee(
            name="ريم محمود",
            role="sales_rep",
            base_salary=5000,
            team_id=team2.id,
            phone="0567890123",
            email="reem@aloud.com",
            hire_date=date(2022, 2, 14)
        )
        
        sales_rep6 = Employee(
            name="يوسف إبراهيم",
            role="sales_rep",
            base_salary=5000,
            team_id=team2.id,
            phone="0578901234",
            email="youssef@aloud.com",
            hire_date=date(2022, 4, 18)
        )
        
        employees = [manager, team_leader1, team_leader2, sales_rep1, sales_rep2, sales_rep3, sales_rep4, sales_rep5, sales_rep6]
        
        for emp in employees:
            db.session.add(emp)
        
        db.session.commit()
        
        # تحديث قادة الفرق
        team1.leader_id = team_leader1.id
        team2.leader_id = team_leader2.id
        db.session.commit()
        
        # إنشاء مؤشرات الأداء
        kpis = [
            PerformanceKPI(name="تحقيق الهدف", description="نسبة تحقيق الهدف الشهري", weight=0.4, max_score=10),
            PerformanceKPI(name="عدد العملاء الجدد", description="عدد العملاء الجدد المكتسبين", weight=0.2, max_score=10),
            PerformanceKPI(name="رضا العملاء", description="تقييم رضا العملاء", weight=0.2, max_score=10),
            PerformanceKPI(name="الالتزام بالتقارير", description="الالتزام بتسليم التقارير في الوقت المحدد", weight=0.1, max_score=10),
            PerformanceKPI(name="التطوير المهني", description="المشاركة في الدورات التدريبية", weight=0.1, max_score=10)
        ]
        
        for kpi in kpis:
            db.session.add(kpi)
        
        db.session.commit()
        
        # إنشاء الأهداف لشهر ديسمبر 2024
        targets_data = [
            (sales_rep1.id, 120000),
            (sales_rep2.id, 120000),
            (sales_rep3.id, 120000),
            (sales_rep4.id, 120000),
            (sales_rep5.id, 120000),
            (sales_rep6.id, 120000),
            (team_leader1.id, 360000),  # مجموع أهداف فريقه
            (team_leader2.id, 360000),  # مجموع أهداف فريقه
            (manager.id, 720000)  # مجموع أهداف جميع الفرق
        ]
        
        for emp_id, target_amount in targets_data:
            target = Target(
                employee_id=emp_id,
                month=12,
                year=2024,
                target_amount=target_amount
            )
            db.session.add(target)
        
        db.session.commit()
        
        # إنشاء مشاريع تجريبية لشهر ديسمبر 2024
        projects_data = [
            # مشاريع الفريق الأول
            (sales_rep1.id, "شركة البناء المتطور", 150000, "حديد إنشائي", False),
            (sales_rep1.id, "مؤسسة الإعمار", 80000, "ألومنيوم", True),
            (sales_rep2.id, "شركة المقاولات الحديثة", 200000, "حديد إنشائي", False),
            (sales_rep2.id, "مكتب الهندسة المعمارية", 60000, "ألومنيوم", True),
            (sales_rep3.id, "شركة التطوير العقاري", 180000, "حديد إنشائي", False),
            (sales_rep3.id, "مؤسسة البناء السريع", 90000, "ألومنيوم", True),
            
            # مشاريع الفريق الثاني
            (sales_rep4.id, "شركة الديكور الفاخر", 140000, "خشب", False),
            (sales_rep4.id, "مكتب التصميم الداخلي", 70000, "حديد ديكور", True),
            (sales_rep5.id, "شركة الأثاث المودرن", 160000, "خشب", False),
            (sales_rep5.id, "معرض الديكور العصري", 85000, "حديد ديكور", True),
            (sales_rep6.id, "شركة التشطيبات الراقية", 170000, "خشب", False),
            (sales_rep6.id, "مؤسسة الديكور الإبداعي", 75000, "حديد ديكور", True)
        ]
        
        for emp_id, client_name, value, product_type, is_social in projects_data:
            project = Project(
                employee_id=emp_id,
                client_name=client_name,
                project_value=value,
                product_type=product_type,
                signature_date=date(2024, 12, random.randint(1, 28)),
                is_from_social_media=is_social,
                notes=f"مشروع تجريبي - {product_type}"
            )
            db.session.add(project)
        
        db.session.commit()
        
        # إنشاء ميزانية التسويق لشهر ديسمبر 2024
        marketing_budget = MarketingBudget(
            month=12,
            year=2024,
            total_budget=50000,
            created_by=manager.id
        )
        db.session.add(marketing_budget)
        db.session.commit()
        
        # إنشاء نقاط أداء تجريبية
        for emp in [sales_rep1, sales_rep2, sales_rep3, sales_rep4, sales_rep5, sales_rep6]:
            for kpi in kpis:
                score = PerformanceScore(
                    employee_id=emp.id,
                    kpi_id=kpi.id,
                    month=12,
                    year=2024,
                    score=random.uniform(6, 10),  # نقاط عشوائية بين 6 و 10
                    notes="تقييم تجريبي"
                )
                score.weighted_score = score.score * kpi.weight
                db.session.add(score)
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء البيانات التجريبية بنجاح',
            'employees_created': len(employees),
            'teams_created': 2,
            'kpis_created': len(kpis),
            'projects_created': len(projects_data),
            'targets_created': len(targets_data)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إنشاء البيانات: {str(e)}'}), 500

