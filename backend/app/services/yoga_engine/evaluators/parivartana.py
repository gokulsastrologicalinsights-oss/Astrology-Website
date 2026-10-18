"""Parivartana Yogas: Maha Parivartana, Kahala Parivartana, and Dainya Parivartana."""

from typing import List, Set, Tuple
from app.schemas.yoga import YogaDetail, YogaConditionItem
from app.services.yoga_engine.models import (
    YogaChartContext,
    SIGN_LORDS,
    OWN_SIGNS,
    SIGN_NAMES_EN,
)

AUSPICIOUS_HOUSES: Set[int] = {1, 2, 4, 5, 7, 9, 10, 11}
DUSTHANA_HOUSES: Set[int] = {6, 8, 12}


def evaluate_parivartana_yogas(ctx: YogaChartContext) -> List[YogaDetail]:
    results: List[YogaDetail] = []
    evaluated_pairs: Set[Tuple[int, int]] = set()

    for h1 in range(1, 13):
        for h2 in range(h1 + 1, 13):
            lord1 = ctx.house_lords[h1]
            lord2 = ctx.house_lords[h2]

            if lord1 == lord2:
                continue

            sign_h1 = ctx.house_to_sign[h1]
            sign_h2 = ctx.house_to_sign[h2]

            sign_lord1 = ctx.planet_sign.get(lord1)
            sign_lord2 = ctx.planet_sign.get(lord2)

            if not sign_lord1 or not sign_lord2:
                continue

            # Classical Parivartana between House h1 and House h2:
            # Lord of h1 occupies the sign of House h2 AND Lord of h2 occupies the sign of House h1
            if sign_lord1 == sign_h2 and sign_lord2 == sign_h1:
                pair_key = (h1, h2)
                if pair_key in evaluated_pairs:
                    continue
                evaluated_pairs.add(pair_key)
                h1_val = ctx.planet_house.get(lord1)
                h2_val = ctx.planet_house.get(lord2)

                # Classify into Maha, Kahala, or Dainya
                is_dainya = (h1 in DUSTHANA_HOUSES or h2 in DUSTHANA_HOUSES)
                is_kahala = not is_dainya and (h1 == 3 or h2 == 3)
                is_maha = not is_dainya and not is_kahala and (h1 in AUSPICIOUS_HOUSES and h2 in AUSPICIOUS_HOUSES)

                if is_maha:
                    y_id = f"maha_parivartana_{lord1.lower()}_{lord2.lower()}"
                    y_name = f"Maha Parivartana Yoga ({lord1} & {lord2})"
                    y_name_ta = f"மகா பரிவர்த்தனை யோகம் ({lord1} & {lord2})"
                    y_cat = "Parivartana"
                    interp = (
                        f"Majestic mutual reception: {lord1} and {lord2} empower houses {h1} and {h2}, "
                        "bestowing wealth, leadership, continuous honor, and prosperity."
                    )
                    classical_def = f"Mutual sign exchange between auspicious house lords ({h1} and {h2})."
                elif is_kahala:
                    y_id = f"kahala_parivartana_{lord1.lower()}_{lord2.lower()}"
                    y_name = f"Kahala Parivartana Yoga ({lord1} & {lord2})"
                    y_name_ta = f"காகல பரிவர்த்தனை யோகம் ({lord1} & {lord2})"
                    y_cat = "Parivartana"
                    interp = (
                        f"Valorous enterprise: 3rd house exchange with {h1 if h2 == 3 else h2} builds resolute courage, "
                        "strategic grit, and success through self-initiative."
                    )
                    classical_def = f"Mutual sign exchange between the 3rd house lord and an auspicious house lord ({h1 if h2 == 3 else h2})."
                else:
                    y_id = f"dainya_parivartana_{lord1.lower()}_{lord2.lower()}"
                    y_name = f"Dainya Parivartana Yoga ({lord1} & {lord2})"
                    y_name_ta = f"தைன்ய பரிவர்த்தனை யோகம் ({lord1} & {lord2})"
                    y_cat = "Parivartana"
                    interp = (
                        f"Karmic transformation: Exchange involving Dusthana lord transforms trials into wisdom and victory "
                        "through disciplined patience."
                    )
                    classical_def = f"Mutual sign exchange involving Dusthana house lords ({h1} and {h2})."

                results.append(
                    YogaDetail(
                        id=y_id,
                        name=y_name,
                        name_tamil=y_name_ta,
                        category=y_cat,
                        status="Qualifying",
                        is_qualifying=True,
                        planets_involved=[lord1, lord2],
                        relevant_houses=[h1_val, h2_val],
                        conditions=[
                            YogaConditionItem(
                                condition=f"{lord1} (rules House {h1}) occupies {lord2}'s sign ({SIGN_NAMES_EN[sign_lord1]})",
                                passed=True,
                                detail=f"{lord1} is in House {h1_val} ({SIGN_NAMES_EN[sign_lord1]})."
                            ),
                            YogaConditionItem(
                                condition=f"{lord2} (rules House {h2}) occupies {lord1}'s sign ({SIGN_NAMES_EN[sign_lord2]})",
                                passed=True,
                                detail=f"{lord2} is in House {h2_val} ({SIGN_NAMES_EN[sign_lord2]})."
                            )
                        ],
                        short_interpretation=interp,
                        classical_definition=classical_def,
                        classical_reference="Phaladeepika Ch. 6, verses 32-43; Brihat Parashara Hora Shastra",
                        verification_status="Classical Independent Implementation"
                    )
                )

    return results
