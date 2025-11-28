from app import create_app
from app.extensions import db, bcrypt
from app.models.v1 import User, Department, Domain, Role

app = create_app("development")

def seed_users():
    with app.app_context():
        if User.query.count() > 0:
            print("Users already seeded!")
            return
        ict_domain = Domain.query.filter_by(name="ICT").first()
        if not ict_domain:
            ict_domain = Domain(name="ICT")
            db.session.add(ict_domain)

        eng_domain = Domain.query.filter_by(name="Engineering").first()
        if not eng_domain:
            eng_domain = Domain(name="Engineering")
            db.session.add(eng_domain)

        db.session.commit()

        default_department = Department.query.first() 
        default_role = Role.query.first()

        user1 = User(
            fullname="BONIFACE MURANGIRI",
            email="bmurangiri@fresha.co.ke",
            password=bcrypt.generate_password_hash("Ict12345!").decode('utf-8'),
            department_id=default_department.id if default_department else None,
            role_id=default_role.id if default_role else None,
            domain_id=ict_domain.id,
            payroll_no="P2068"
        )

        user2 = User(
            fullname="MURANGIRI NJERU",
            email="bonnyrangi95@gmail.com",
            password=bcrypt.generate_password_hash("Eng12345!").decode('utf-8'),
            department_id=default_department.id if default_department else None,
            role_id=default_role.id if default_role else None,
            domain_id=eng_domain.id,
            payroll_no="P2070"
        )

        db.session.add_all([user1, user2])
        db.session.commit()
        print("Seeded initial users successfully!")

if __name__ == "__main__":
    seed_users()
