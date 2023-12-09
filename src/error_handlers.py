from flask import flash, redirect, url_for

# Error handling for basic error codes, needs to be updated
def handle_internal_server_error(e):
    flash('Error 500 - Wystąpił błąd w aplikacji.', 'danger')
    return redirect(url_for('main_routes.home'))



def handle_not_found_error(e):
    flash('Error 404 - Strona nie została znaleziona.', 'danger')
    return redirect(url_for('main_routes.home'))


def handle_forbidden_error(e):
    flash('Error 403 - Brak dostępu do tej strony.', 'danger')
    return redirect(url_for('main_routes.home'))

def handle_unauthorized_error(e):
    flash('Error 401 - Brak autoryzacji do dostępu do tej strony.', 'danger')
    return redirect(url_for('main_routes.home'))