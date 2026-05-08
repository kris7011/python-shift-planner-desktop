from app.personalized_workload import calculate_personalized_workload_score


def explain_assignment(shift, employee, profile) -> list[str]:
    explanations = []

    explanations.append(f"{employee} has required skill: {shift.required_skill}")

    if profile is None:
        explanations.append("No employee profile found")
        return explanations

    score = calculate_personalized_workload_score(shift, profile)

    explanations.append(f"Personalized workload score: {score:.1f}")
    explanations.append(f"Preferred shift: {profile.preferred_shift.value}")

    if shift.shift_type == profile.preferred_shift:
        explanations.append("Shift matches employee preference")

    return explanations