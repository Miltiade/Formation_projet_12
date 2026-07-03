from app.controllers.authentication import UserManager

def main():
    manager = UserManager()
    
    # Création d'un utilisateur test
    user_created = manager.create_user(
        id=1,
        username="alice",
        email="alice@example.com",
        password="TestPass123!",
        department_name="Gestion"
    )
    print("Utilisateur créé :", user_created.username, user_created.email)

    # Tentative d'authentification avec un mot de passe erroné
    user_auth_fail = manager.authenticate("alice@example.com", "WrongPass!")
    print("Authentification avec mauvais mot de passe :", "Succès" if user_auth_fail else "Échec")

    # Tentative d'authentification avec le bon mot de passe
    user_auth = manager.authenticate("alice@example.com", "TestPass123!")
    if user_auth:
        print(f"Authentification réussie pour {user_auth.username}")
    else:
        print("Échec de l’authentification")

    # Récupérer tous les utilisateurs
    all_users = manager.get_all_users()
    print(f"Nombre total d’utilisateurs en base : {len(all_users)}")
    for user in all_users:
        print(f"- {user.username} ({user.email})")

if __name__ == "__main__":
    main()