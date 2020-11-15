from django.contrib.auth.decorators import login_required, user_passes_test


instructor_role = user_passes_test(lambda u: True if u.is_instructor else False)
def instructor_required(view_func):
    decorated_view_func = login_required(instructor_role(view_func))
    return decorated_view_func


learner_role = user_passes_test(lambda u: True if u.is_learner else False)
def learner_required(view_func):
    decorated_view_func = login_required(learner_role(view_func))
    return decorated_view_func
