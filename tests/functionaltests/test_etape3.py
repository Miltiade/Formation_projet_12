from argon2 import PasswordHasher
from app.models.classes import Collaborator, Department
from app.controllers.authentication import UserManager
from app.controllers.authorizations import get_permissions, has_permission

def run_test(test_func):
    print(f"Début du test : {test_func.__name__} ...")
    try:
        test_func()
        print(f"✅ Succès : {test_func.__name__}\n")
    except AssertionError as e:
        print(f"❌ Échec : {test_func.__name__} - {e}\n")
    except Exception as e:
        print(f"❌ Exception inattendue dans {test_func.__name__} - {e}\n")

def test_department_role_mapping():
    dept = Department("Gestion")
    assert dept.role == "gestion", "Erreur rôle Gestion :("
    dept = Department("Commercial")
    assert dept.role == "commercial", "Erreur rôle Commercial :("
    dept = Department("Support")
    assert dept.role == "support", "Erreur rôle Support :("
    try:
        Department("Finance")
        assert False, "Department invalide accepté :("
    except ValueError:
        pass  # OK

def test_collaborator_attributes_and_password_hashing():
    password = "monSuperMDP123!"
    user = Collaborator(1, "alice", "alice@example.com", password, Department("Gestion"))
    assert user.id == 1
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.department.name == "Gestion"
    assert user.role == "gestion"
    assert user._Collaborator__password_hash != password, "Mot de passe stocké en clair :("
    assert user.verify_password(password), "La vérification du mot de passe a échoué :("
    assert not user.verify_password("fauxmdp"), "Mot de passe incorrect validé :("

def test_user_creation_and_authentication():
    manager = UserManager()
    created = manager.create_user(42, "bob", "bob@example.com", "MotDePasse!", "Commercial")
    assert created.username == "bob"
    assert created.department.name == "Commercial"
    auth = manager.authenticate("bob@example.com", "MotDePasse!")
    assert auth is not None, "Authentification a échoué avec bon mot de passe :("
    assert auth.username == "bob"
    assert auth.role == "commercial"
    assert manager.authenticate("bob@example.com", "mauvaismdp") is None, "Authentification réussie avec mauvais mdp :("
    assert manager.authenticate("inconnu@example.com", "MotDePasse!") is None, "Authentification réussie avec email inconnu :("

def test_permissions_roles():
    for name, expected_role in [("Gestion", "gestion"), ("Commercial", "commercial"), ("Support", "support")]:
        d = Department(name)
        u = Collaborator(0, "test", "t@example.com", "p", d)
        perms = get_permissions(u)
        assert isinstance(perms, list), f"Permissions doivent être une liste pour {name} :("
        assert all(isinstance(p, str) for p in perms), f"Permissions non string pour {name}"
        if perms:
            assert has_permission(u, perms[0]), f"Permission {perms[0]} manquante pour {name} :("
        assert not has_permission(u, "permission_inexistante"), f"Permission inexistante détectée pour {name} :("

def main():
    tests = [
        test_department_role_mapping,
        test_collaborator_attributes_and_password_hashing,
        test_user_creation_and_authentication,
        test_permissions_roles,
    ]
    print("Lancement des tests minimalistes avec messages clairs\n")
    for test in tests:
        run_test(test)
    print("Fin des tests.")

if __name__ == "__main__":
    main()