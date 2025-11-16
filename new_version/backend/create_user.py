from models import get_db, User

db = get_db()

# Check if user exists
existing_user = db.query(User).filter(User.name == 'Tousif').first()

if existing_user:
    print(f"✅ User already exists with ID: {existing_user.id}")
else:
    user = User(
        name='Dhanush',
        email='annhilatordc@gmail.com', 
        face_id='dhanush'
    )
    
    db.add(user)
    db.commit()
    print(f"✅ User created with ID: {user.id}")

db.close()