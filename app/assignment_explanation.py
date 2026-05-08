from app.personalized_workload import calculate_personalized_workload_score


def explain_assignment(shift, employee, profile) -> list[str]:
    explanations = []

    explanations.append(f"{employee} har den krævede kompetence: {shift.required_skill}")

    if profile is None:
        explanations.append("Ingen medarbejderprofil fundet")
        return explanations

    score = calculate_personalized_workload_score(shift, profile)

    explanations.append(f"Personlig belastningsscore: {score:.1f}")
    explanations.append(f"Foretrukken vagttype: {profile.preferred_shift.value}")

    if shift.shift_type == profile.preferred_shift:
        explanations.append("Vagten matcher medarbejderens foretrukne vagttype")

    return explanations