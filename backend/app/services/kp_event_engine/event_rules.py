"""KP Event Prediction Engine - Event Definitions & Centralized Registry.

Defines the 32 standard KP events, their supporting (S) and denying (D) houses,
primary cusps for Cuspal Sub-Lord (CSL) evaluation, gain-type classifications,
and standardized cautious prediction hints (<= 20 words each).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

RULE_SET_VERSION = "1.0.0"


@dataclass(frozen=True)
class EventRule:
    """Configuration for a specific KP astrological event."""
    name: str
    category: str
    supporting_houses: List[int]
    denying_houses: List[int]
    primary_cusp: int
    is_gain_type: bool
    green_hint: str
    orange_hint: str
    red_hint: str
    description: str = ""

    def get_hint(self, color: str) -> str:
        c = color.lower()
        if c == "green":
            return self.green_hint
        elif c == "orange":
            return self.orange_hint
        return self.red_hint


# Centralized 32 KP Events as formally defined in Section 5
EVENT_REGISTRY: Dict[str, EventRule] = {
    "Marriage": EventRule(
        name="Marriage",
        category="Relationship",
        supporting_houses=[2, 7, 11],
        denying_houses=[1, 6, 10],
        primary_cusp=7,
        is_gain_type=False,
        green_hint="A marriage proposal appears possible; consider following up on suitable opportunities.",
        orange_hint="Marriage discussions are possible, though some delays or compromises may be required.",
        red_hint="Conditions for marriage appear limited during this period; patience is advised.",
        description="Legal marriage union and matrimonial commitment.",
    ),
    "Love affair": EventRule(
        name="Love affair",
        category="Relationship",
        supporting_houses=[5, 7, 11],
        denying_houses=[1, 6, 10],
        primary_cusp=5,
        is_gain_type=False,
        green_hint="A romance or romantic connection may blossom favorably during this period.",
        orange_hint="Romantic interests may emerge, though emotional clarity and patience are suggested.",
        red_hint="Emotional bonding may face friction or misunderstandings during this phase.",
        description="Courtship, mutual attraction, and romantic bond.",
    ),
    "Second marriage": EventRule(
        name="Second marriage",
        category="Relationship",
        supporting_houses=[2, 7, 9, 11],
        denying_houses=[1, 6, 8, 10],
        primary_cusp=9,
        is_gain_type=False,
        green_hint="Favorable indications for a second union or fresh partnership may unfold.",
        orange_hint="Second marriage discussions may progress gradually with due family alignment.",
        red_hint="Prospects for a second marital alliance appear restrained in this period.",
        description="Remarriage or secondary matrimonial alliance.",
    ),
    "Divorce / separation": EventRule(
        name="Divorce / separation",
        category="Relationship",
        supporting_houses=[1, 6, 10, 12],
        denying_houses=[2, 7, 11],
        primary_cusp=6,
        is_gain_type=False,
        green_hint="Significant separation or legal dissolution indicators are strong in this period.",
        orange_hint="Marital strain or temporary physical separation is indicated; mediation is helpful.",
        red_hint="Separation impulses appear weak; reconciliation remains achievable.",
        description="Marital estrangement, separation, or legal dissolution.",
    ),
    "Children": EventRule(
        name="Children",
        category="Family",
        supporting_houses=[2, 5, 11],
        denying_houses=[1, 4, 10],
        primary_cusp=5,
        is_gain_type=False,
        green_hint="Childbirth or favorable progeny news appears strongly supported in this period.",
        orange_hint="Conception or child-related developments may progress with routine medical care.",
        red_hint="Childbirth prospects appear delayed; medical guidance and timing may help.",
        description="Conception, progeny blessings, and birth of a child.",
    ),
    "Miscarriage": EventRule(
        name="Miscarriage",
        category="Health",
        supporting_houses=[4, 8, 10],
        denying_houses=[2, 5, 11],
        primary_cusp=8,
        is_gain_type=False,
        green_hint="High caution advised regarding pregnancy health; timely rest and medical advice essential.",
        orange_hint="Moderate health sensitivity during pregnancy; precautionary medical care is advised.",
        red_hint="Pregnancy vulnerability indicators appear low during this period.",
        description="Threat to pregnancy or unexpected termination.",
    ),
    "Job": EventRule(
        name="Job",
        category="Career",
        supporting_houses=[2, 6, 10, 11],
        denying_houses=[1, 5, 9],
        primary_cusp=6,
        is_gain_type=True,
        green_hint="A promising new employment or career breakthrough appears very likely.",
        orange_hint="A job opportunity appears possible, although some delays may occur.",
        red_hint="Job search efforts may require sustained patience and preparation.",
        description="New employment, placement, or career commencement.",
    ),
    "Promotion": EventRule(
        name="Promotion",
        category="Career",
        supporting_houses=[2, 6, 10, 11],
        denying_houses=[5, 8, 9, 12],
        primary_cusp=10,
        is_gain_type=True,
        green_hint="Career advancement, elevation in role, or organizational recognition is strongly indicated.",
        orange_hint="Promotion opportunities may arise, subject to organizational timelines or reviews.",
        red_hint="Advancement in rank may face procedural hurdles or delays currently.",
        description="Elevation in designation, hierarchy, or salary.",
    ),
    "Transfer": EventRule(
        name="Transfer",
        category="Career",
        supporting_houses=[3, 10, 12],
        denying_houses=[2, 4, 11],
        primary_cusp=10,
        is_gain_type=False,
        green_hint="A professional transfer, relocation, or departmental change appears favorable.",
        orange_hint="Workplace transfer or movement is possible, though logistics may require adaptation.",
        red_hint="Relocation or official transfer indications appear minimal in this period.",
        description="Official relocation or job department transfer.",
    ),
    "Job loss": EventRule(
        name="Job loss",
        category="Career",
        supporting_houses=[1, 5, 8, 9, 12],
        denying_houses=[2, 6, 10, 11],
        primary_cusp=10,
        is_gain_type=False,
        green_hint="Employment instability or sudden transition is strongly indicated; exercise caution.",
        orange_hint="Workplace changes or role friction may arise; maintain professional composure.",
        red_hint="Job security remains largely stable; risk of involuntary exit is low.",
        description="Involuntary termination, layoff, or career suspension.",
    ),
    "Business start": EventRule(
        name="Business start",
        category="Career",
        supporting_houses=[2, 7, 10, 11],
        denying_houses=[1, 5, 9],
        primary_cusp=7,
        is_gain_type=True,
        green_hint="Commercial ventures or independent business initiatives find strong planetary backing.",
        orange_hint="New enterprise launch is viable with prudent capital planning and due diligence.",
        red_hint="New business launch may face initial inertia; consolidate plans first.",
        description="Commencement of an enterprise, company, or independent trade.",
    ),
    "Partnership": EventRule(
        name="Partnership",
        category="Career",
        supporting_houses=[2, 7, 10, 11],
        denying_houses=[1, 6, 12],
        primary_cusp=7,
        is_gain_type=False,
        green_hint="Forming mutually rewarding commercial or professional alliances appears favorable.",
        orange_hint="Partnership agreements may proceed, provided roles and equity terms are clear.",
        red_hint="Collaborative ventures may lack synergy; independent operation is preferable.",
        description="Commercial partnership, co-founding, or joint alliance.",
    ),
    "Government job": EventRule(
        name="Government job",
        category="Career",
        supporting_houses=[2, 6, 10, 11],
        denying_houses=[5, 8, 9, 12],
        primary_cusp=10,
        is_gain_type=True,
        green_hint="Success in public sector appointments or state examinations is strongly indicated.",
        orange_hint="Government selection is possible through dedicated effort and timely application.",
        red_hint="Public sector entry may face tight competition and procedural delays.",
        description="Appointment in state, civil, or federal government service.",
    ),
    "Financial gain": EventRule(
        name="Financial gain",
        category="Finance",
        supporting_houses=[2, 6, 11],
        denying_houses=[5, 8, 12],
        primary_cusp=11,
        is_gain_type=True,
        green_hint="Substantial wealth inflow, profit realization, or financial prosperity is indicated.",
        orange_hint="Moderate financial inflows and earnings are likely with disciplined budgeting.",
        red_hint="Major financial gains appear limited; focus on steady capital conservation.",
        description="Inflow of money, trade earnings, and monetary growth.",
    ),
    "Loan taken": EventRule(
        name="Loan taken",
        category="Finance",
        supporting_houses=[6, 11],
        denying_houses=[5, 12],
        primary_cusp=6,
        is_gain_type=True,
        green_hint="Credit sanction, mortgage approval, or commercial loan disbursement is favored.",
        orange_hint="Loan acquisition is possible with routine verification and structured paperwork.",
        red_hint="Borrowing or institutional credit approvals may face administrative delays.",
        description="Successful borrowing, debt sanction, or bank credit.",
    ),
    "Loan repayment": EventRule(
        name="Loan repayment",
        category="Finance",
        supporting_houses=[5, 8, 12],
        denying_houses=[6, 11],
        primary_cusp=5,
        is_gain_type=False,
        green_hint="Substantial debt settlement or mortgage discharge appears achievable now.",
        orange_hint="Steady progress toward clearing liabilities is supported during this period.",
        red_hint="Debt liquidation may require stricter expenditure control and time.",
        description="Clearing debts, loan payoff, or mortgage freedom.",
    ),
    "Speculation / lottery": EventRule(
        name="Speculation / lottery",
        category="Finance",
        supporting_houses=[2, 5, 8, 11],
        denying_houses=[4, 10, 12],
        primary_cusp=5,
        is_gain_type=True,
        green_hint="High-yield speculative returns or trading windfalls appear strongly supported.",
        orange_hint="Calculated speculative trading may yield modest profits; manage downside risk.",
        red_hint="Speculative investments carry notable risk of capital erosion; caution advised.",
        description="Stock market windfalls, lotteries, or speculative gains.",
    ),
    "Inheritance / insurance": EventRule(
        name="Inheritance / insurance",
        category="Finance",
        supporting_houses=[2, 8, 11],
        denying_houses=[1, 7, 12],
        primary_cusp=8,
        is_gain_type=True,
        green_hint="Receipt of ancestral wealth, insurance claims, or legacy assets is favored.",
        orange_hint="Inheritance or policy disbursements may materialize after statutory formalities.",
        red_hint="Resolution of legacy or claim benefits appears delayed in this period.",
        description="Unearned wealth, inheritance, or insurance payout.",
    ),
    "Higher education": EventRule(
        name="Higher education",
        category="Education",
        supporting_houses=[4, 9, 11],
        denying_houses=[3, 8, 12],
        primary_cusp=9,
        is_gain_type=False,
        green_hint="Academic milestones, university admissions, or advanced scholarly success is favored.",
        orange_hint="Academic progress is likely with focused discipline and structured revisions.",
        red_hint="Progress may need additional preparation before a stronger period.",
        description="University degree, masters, doctorate, or scholarly elevation.",
    ),
    "Competitive exam": EventRule(
        name="Competitive exam",
        category="Education",
        supporting_houses=[6, 10, 11],
        denying_houses=[5, 8, 12],
        primary_cusp=6,
        is_gain_type=True,
        green_hint="High percentile or merit list standing in competitive evaluations is indicated.",
        orange_hint="Competitive examination results may be positive with methodical preparation.",
        red_hint="Competitive entrance tests require enhanced focus and second attempts.",
        description="Competitive entrance exams, recruitment screenings, or olympiads.",
    ),
    "Foreign travel": EventRule(
        name="Foreign travel",
        category="Travel",
        supporting_houses=[3, 9, 12],
        denying_houses=[2, 11],
        primary_cusp=12,
        is_gain_type=False,
        green_hint="Overseas journeys, visa grants, or international excursions appear favored.",
        orange_hint="Foreign travel plans may proceed, though itinerary schedules may adjust.",
        red_hint="International travel opportunities appear dormant or postponed currently.",
        description="Short or long overseas journey and international travel.",
    ),
    "Settlement abroad": EventRule(
        name="Settlement abroad",
        category="Travel",
        supporting_houses=[3, 9, 12],
        denying_houses=[2, 11],
        primary_cusp=12,
        is_gain_type=False,
        green_hint="Permanent overseas relocation or permanent residency grants are strongly indicated.",
        orange_hint="Immigration processes may advance gradually through regulatory steps.",
        red_hint="Permanent foreign residency indications appear weak in this phase.",
        description="Permanent overseas immigration or citizen residency.",
    ),
    "Property purchase": EventRule(
        name="Property purchase",
        category="Property",
        supporting_houses=[4, 11, 12],
        denying_houses=[3, 10],
        primary_cusp=4,
        is_gain_type=False,
        green_hint="Acquisition of real estate, land parcels, or residential property is favored.",
        orange_hint="Real estate investments may progress with careful title scrutiny.",
        red_hint="Property buying decisions may encounter price negotiations or delays.",
        description="Buying residential house, apartment, or land.",
    ),
    "Property sale": EventRule(
        name="Property sale",
        category="Property",
        supporting_houses=[3, 5, 10],
        denying_houses=[4, 11, 12],
        primary_cusp=10,
        is_gain_type=False,
        green_hint="Profitable sale or disposal of fixed assets and real estate is supported.",
        orange_hint="Property liquidation is feasible with reasonable pricing flexibility.",
        red_hint="Real estate disposal may take longer to attract suitable buyers.",
        description="Disposal or profitable liquidation of land or house.",
    ),
    "Vehicle purchase": EventRule(
        name="Vehicle purchase",
        category="Property",
        supporting_houses=[4, 11, 12],
        denying_houses=[3, 10],
        primary_cusp=4,
        is_gain_type=False,
        green_hint="Purchase or upgrade of an automobile or conveyance appears favored.",
        orange_hint="Vehicle acquisition is achievable with planned financing and choice.",
        red_hint="Vehicle buying plans may be deferred to a more auspicious period.",
        description="Buying car, motorcycle, or conveyance.",
    ),
    "Change of residence": EventRule(
        name="Change of residence",
        category="Property",
        supporting_houses=[3, 4, 12],
        denying_houses=[2, 11],
        primary_cusp=4,
        is_gain_type=False,
        green_hint="Relocation to a new domicile or tenancy transition is strongly supported.",
        orange_hint="Residential shifting is possible with adequate packing and planning.",
        red_hint="Domestic relocation impulses appear subdued in this period.",
        description="Moving home, tenancy change, or house shifting.",
    ),
    "Illness": EventRule(
        name="Illness",
        category="Health",
        supporting_houses=[1, 6, 8, 12],
        denying_houses=[5, 11],
        primary_cusp=6,
        is_gain_type=False,
        green_hint="Health vulnerability is elevated; prompt medical diagnosis and care are prudent.",
        orange_hint="Minor health fatigue or recurrent ailments may require lifestyle adjustments.",
        red_hint="General vitality remains sound; resistance against major illness is strong.",
        description="Manifestation of sickness, disease, or medical disorder.",
    ),
    "Recovery": EventRule(
        name="Recovery",
        category="Health",
        supporting_houses=[1, 5, 11],
        denying_houses=[6, 8, 12],
        primary_cusp=11,
        is_gain_type=False,
        green_hint="Rapid recuperation, vitality restoration, and positive therapy outcomes are indicated.",
        orange_hint="Health improvements may occur steadily with adherence to prescribed regimen.",
        red_hint="Convalescence may take time; rest and continuous care are necessary.",
        description="Overcoming illness, healing, and restoration of vigor.",
    ),
    "Litigation win": EventRule(
        name="Litigation win",
        category="Legal",
        supporting_houses=[1, 6, 11],
        denying_houses=[5, 8, 12],
        primary_cusp=6,
        is_gain_type=True,
        green_hint="Favorable legal verdict, court decree, or dispute resolution is strongly supported.",
        orange_hint="Legal arguments may lean in your favor, though final decree may require time.",
        red_hint="Dispute proceedings may face counterclaims; out-of-court settlement is wise.",
        description="Success in court trials, lawsuits, or arbitration.",
    ),
    "Litigation loss": EventRule(
        name="Litigation loss",
        category="Legal",
        supporting_houses=[5, 8, 12],
        denying_houses=[1, 6, 11],
        primary_cusp=12,
        is_gain_type=False,
        green_hint="Adverse judicial outcome or penalties indicated; strategic compromise is advised.",
        orange_hint="Legal contentions carry moderate risk; expert counsel is recommended.",
        red_hint="Adverse legal risks appear minimal during this planetary period.",
        description="Adverse verdict, court penalty, or trial defeat.",
    ),
    "Imprisonment": EventRule(
        name="Imprisonment",
        category="Legal",
        supporting_houses=[6, 8, 12],
        denying_houses=[1, 5, 11],
        primary_cusp=12,
        is_gain_type=False,
        green_hint="Severe legal restraint or confinement risk; strict statutory compliance essential.",
        orange_hint="Regulatory restrictions or administrative confinement require close compliance.",
        red_hint="Indications of personal confinement or custody are negligible.",
        description="Incarceration, judicial remand, or state custody.",
    ),
    "Spiritual / pilgrimage": EventRule(
        name="Spiritual / pilgrimage",
        category="Spirituality",
        supporting_houses=[5, 9, 12],
        denying_houses=[2, 6, 10],
        primary_cusp=9,
        is_gain_type=False,
        green_hint="Sacred pilgrimages, spiritual initiation, or meditative realization is favored.",
        orange_hint="Spiritual inclinations and religious visits may proceed with quiet devotion.",
        red_hint="Spiritual journeys may take a backseat to mundane responsibilities.",
        description="Holy shrine visits, deeksha, mantra initiation, and inner retreat.",
    ),
    "Critical longevity / Maraka period": EventRule(
        name="Critical longevity / Maraka period",
        category="Health",
        supporting_houses=[2, 7, 8, 12],
        denying_houses=[1, 5, 11],
        primary_cusp=8,
        is_gain_type=False,
        green_hint="Heightened longevity vulnerability and Maraka-Badhaka operational phase; remedial health care strongly advised.",
        orange_hint="Health sensitivity requires preventive wellness care and prudent medical attention.",
        red_hint="Vitality remains safeguarded by benevolent life-affirming houses (1, 5, 11).",
        description="Critical longevity evaluation, maraka-badhaka periods, and acute life vulnerability.",
    ),
    "Accident / Surgery": EventRule(
        name="Accident / Surgery",
        category="Health",
        supporting_houses=[6, 8, 12],
        denying_houses=[1, 5, 11],
        primary_cusp=8,
        is_gain_type=False,
        green_hint="Elevation in accident or surgical intervention indicators; cautionary lifestyle and road safety advised.",
        orange_hint="Mild risk of minor injury or routine medical procedure; standard precautions suffice.",
        red_hint="Negligible indicators for accidents, traumatic injuries, or surgical intervention.",
        description="Accidental physical trauma, surgeries, or unexpected medical intervention.",
    ),
}

GAIN_TYPE_EVENTS: Set[str] = {
    name for name, rule in EVENT_REGISTRY.items() if rule.is_gain_type
}


def get_event_rule(event_name: str) -> Optional[EventRule]:
    """Retrieve an event rule by name, case-insensitively."""
    for name, rule in EVENT_REGISTRY.items():
        if name.lower() == event_name.lower().strip():
            return rule
    return None


def list_all_events() -> List[EventRule]:
    """List all registered KP events in canonical order."""
    return list(EVENT_REGISTRY.values())


def get_events_by_category(category: str) -> List[EventRule]:
    """Filter events by category name."""
    c_lower = category.lower().strip()
    return [e for e in EVENT_REGISTRY.values() if e.category.lower() == c_lower]
