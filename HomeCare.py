import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)
from telegram.ext.filters import TEXT, COMMAND

# Define all conversation states
(
    MAIN_MENU,              # 0

    VITAL_SIGNS_MENU,       # 1
    ENTER_VITAL_SIGN_VALUE, # 2

    ENTER_PAIN_SCORE,       # 3
    ENTER_PAIN_LOCATION,    # 4
    ENTER_PAIN_TYPE,        # 5
    ENTER_PAIN_SYMPTOMS,    # 6

    RESPIRATORY_SYSTEM,     # 7

    GASTROINTESTINAL_SYSTEM,# 8
    
    CONSCIOUSNESS,          # 9

    EMOTIONAL_STATUS_MENU,  # 10
    ENTER_EMOTIONAL_STATUS, # 11

    PROBLEM_MENU,            #12
    ENTER_PROBLEM_DESCRIPTION, #13

    WOUND_HEALING_MENU,     # 14
    ENTER_WOUND_INFO,       # 15

    SLEEP_PATTERN,          # 16
    SLEEP_POSITION,         # 17 

    QOR_ASSESSMENT_MENU,    #18
    ENTER_QOR_RESPONSE,     # 19

    DOCTOR_ALERT           # 20
) = range(21)

# Doctor chat ID (set your actual doctor's chat ID here)
DOCTOR1_CHAT_ID = "1560401585" #ilker
DOCTOR2_CHAT_ID = "151797397" #Amr: 

# Safe ranges for parameters
PARAMETER_RANGES = {
    "heart_rate": {"min": 50, "max": 140, "unit": "/min"},
    "systolic_blood_pressure": {"min": 60, "max": 190, "unit": "mmHg"},
    "diastolic_blood_pressure": {"min": 40, "max": 100, "unit": "mmHg"},
    "respiration_rate": {"max": 30, "unit": "/min"},
    "temperature": {"max": 37.5, "unit": "°C"},
}

# Patient data storage
DATA_DIR = "patient_data"
os.makedirs(DATA_DIR, exist_ok=True)

# ======================
# KEYBOARD DEFINITIONS
# ======================

def main_menu_keyboard():
    """Create the main menu keyboard with all options from the Word doc"""
    return [
        [InlineKeyboardButton("1. Vital Signs", callback_data='vital_signs')],
        [InlineKeyboardButton("2. Pain Assessment", callback_data='pain')],
        [InlineKeyboardButton("3. Respiratory System", callback_data='respiratory')],
        [InlineKeyboardButton("4. Gastrointestinal", callback_data='gastrointestinal')],
        [InlineKeyboardButton("5. Consciousness", callback_data='consciousness')],
        [InlineKeyboardButton("6. Emotional Status", callback_data='emotional_status')],
        [InlineKeyboardButton("7. Medication Compliance", callback_data='medication_compliance')],
        [InlineKeyboardButton("8. Wound Healing", callback_data='wound_healing')],
        [InlineKeyboardButton("9. Post-op Adaptation", callback_data='postop_adaptation')],
        [InlineKeyboardButton("10. Stocking Socks Use", callback_data='stocking_socks')],
        [InlineKeyboardButton("11. Diet Compliance", callback_data='diet_compliance')],
        [InlineKeyboardButton("12. Activity Adaptation", callback_data='activity_adaptation')],
        [InlineKeyboardButton("13. Daily Mobilization", callback_data='daily_mobilization')],
        [InlineKeyboardButton("14. Social Life Adaptation", callback_data='social_adaptation')],
        [InlineKeyboardButton("15. Shower", callback_data='shower')],
        [InlineKeyboardButton("16. Return to Work", callback_data='return_to_work')],
        [InlineKeyboardButton("17. Driving", callback_data='driving')],
        [InlineKeyboardButton("18. Sleep Pattern", callback_data='sleep_pattern')],
        [InlineKeyboardButton("19. Sleeping Position", callback_data='sleep_position')],
        [InlineKeyboardButton("20. Postoperative Quality of Recovery", callback_data='postoperative_quality_of_recovery')]
    ]

def back_only_keyboard(target):
    return [[InlineKeyboardButton("◀ Back", callback_data=f'back_to_{target}')]]

def problem_menu_keyboard():
    return [
        [InlineKeyboardButton("No problem", callback_data='no_problem')],
        [InlineKeyboardButton("There is a problem", callback_data='problem')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

# ======================
# HANDLER FUNCTIONS
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and show main menu."""
    user = update.message.from_user
    context.user_data['patient_id'] = user.id
    
    await update.message.reply_text(
        "🏥 Home Care Monitoring\nPlease select a parameter to report:",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
    )
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle all main menu options from the Word doc"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'vital_signs':
        reply_markup = InlineKeyboardMarkup(vital_signs_menu_keyboard())
        await query.edit_message_text(
            text="Select vital sign to report:",
            reply_markup=reply_markup
        )
        return VITAL_SIGNS_MENU
    
    elif query.data == 'pain':
        await query.edit_message_text(
            "What is your pain score numerical rating (0 - 10)?\n"
            "(0 = No pain, 5 = Moderate pain, 10 = Worst possible pain)",
            reply_markup=InlineKeyboardMarkup(back_only_keyboard('main'))
        )
        return ENTER_PAIN_SCORE
    
    elif query.data == 'respiratory':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(respiratory_menu_keyboard())
        await query.edit_message_text(
            "Do you breathe well or there is a problem?\n",
            reply_markup=reply_markup
        )
        return RESPIRATORY_SYSTEM
    
    elif query.data == 'gastrointestinal':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(gastrointestinal_menu_keyboard())
        await query.edit_message_text(
            "Do you eat well or there is a problem?\n",
            reply_markup=reply_markup
        )
        return GASTROINTESTINAL_SYSTEM
    
    elif query.data == 'consciousness':
        await query.edit_message_text(
            "Describe your alertness level:\n"
            "(e.g., fully alert, drowsy, confused)\n"
            "OR are you oriented to time, place, and person?\n"
            "(e.g., 'I know who/where/when I am')\n"
            "Reply with Okay(Open conscious), confused or unresposive",
            reply_markup=InlineKeyboardMarkup(back_only_keyboard('main'))
        )
        return CONSCIOUSNESS
    
    elif query.data == 'emotional_status':
        await query.edit_message_text(
            "How would you describe your emotional state today?\n"
            "(e.g., anxious, calm, depressed, happy)",
            reply_markup=InlineKeyboardMarkup(back_only_keyboard('main'))
        )
        return EMOTIONAL_STATUS_MENU
        
    elif query.data == 'medication_compliance':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "Have you taken all medications as prescribed today?\n",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
        
    elif query.data == 'wound_healing':
        reply_markup = InlineKeyboardMarkup(wound_healing_menu_keyboard())
        await query.edit_message_text(
            "Choose any of the following issues related to wound healing.?\n",
            reply_markup=reply_markup
        )
        return WOUND_HEALING_MENU
        
    elif query.data == 'postop_adaptation':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "How are you adapting to post-operative requirements?\n"
            "(Please describe if there are any problems)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
    
    elif query.data == 'stocking_socks':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "Have you been using your compression stockings as recommended?\n"
            "(Please describe usage duration if there are any problems)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
        
    elif query.data == 'diet_compliance':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "How is your diet compliance?\n"
            "(Please describe what you've eaten and any issues)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
        
    elif query.data == 'activity_adaptation':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "How are you adapting to recommended activity levels?\n"
            "(Describe your activities and any difficulties)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
        
    elif query.data == 'daily_mobilization':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "Describe your daily mobility:\n"
            "(How often do you get up and move around?)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
        
    elif query.data == 'social_adaptation':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "How are you adapting socially since your procedure?\n"
            "(Describe any social activities or isolation)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
        
    elif query.data == 'shower':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "Have you been able to shower independently?\n"
            "(Describe any difficulties)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU
        
    elif query.data == 'return_to_work':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "What is your status regarding returning to work?\n"
            "(Describe any plans or limitations)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU

    elif query.data == 'driving':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(problem_menu_keyboard())
        await query.edit_message_text(
            "Have you been driving your car normally?\n"
            "(Please describe if there are any problems)",
            reply_markup=reply_markup
        )
        return PROBLEM_MENU

    elif query.data == 'sleep_pattern':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(sleep_pattern_menu_keyboard())
        await query.edit_message_text(
            "Do you sleep normally or there is a problem?\n",
            reply_markup=reply_markup
        )
        return SLEEP_PATTERN
        
    elif query.data == 'sleep_position':
        context.user_data['current_parameter'] = query.data
        reply_markup = InlineKeyboardMarkup(sleep_position_menu_keyboard())
        await query.edit_message_text(
            "What position do you typically sleep in?\n"
            "(e.g., on back, side sleeping, with pillows)",
            reply_markup=reply_markup
        )
        return SLEEP_POSITION
    
    elif query.data == 'postoperative_quality_of_recovery':
        await query.edit_message_text(
            "How have you been feeling in the last 24 hours?\n"
            "(e.g., 0 = worth, 10 = happy)",
            reply_markup=InlineKeyboardMarkup(back_only_keyboard('main'))
        )
        return QOR_ASSESSMENT_MENU
    
    return MAIN_MENU

# ======================
# COMPLETE HANDLER IMPLEMENTATIONS
# ======================
# 1. Vital signs
def vital_signs_menu_keyboard():
    return [
        [InlineKeyboardButton("Heart Rate/ Cadiac Rhythm", callback_data='heart_rate')],
        [InlineKeyboardButton("Systolic Blood Pressure", callback_data='systolic_blood_pressure')],
        [InlineKeyboardButton("Diastolic Blood Pressure", callback_data='diastolic_blood_pressure')],
        [InlineKeyboardButton("Temperature/Fever", callback_data='temperature')],
        [InlineKeyboardButton("Respiration Rate", callback_data='respiration_rate')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

async def vital_signs_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle vital signs menu navigation."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_main':
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU
    
    # Store selected vital sign
    context.user_data['current_vital'] = query.data
    param_info = PARAMETER_RANGES.get(query.data, {})
    
    # Prepare range info
    range_text = ""
    if 'min' in param_info and 'max' in param_info:
        range_text = f" (normal range: {param_info['min']}-{param_info['max']}{param_info['unit']})"
    elif 'max' in param_info:
        range_text = f" (max: {param_info['max']}{param_info['unit']})"
    await query.edit_message_text(
        f"Please enter your {query.data.replace('_', ' ')}{range_text}:",
        reply_markup=InlineKeyboardMarkup(back_only_keyboard('vital_signs'))
    )
    return ENTER_VITAL_SIGN_VALUE

async def enter_vital_sign_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process entered vital sign value."""
    user_id = context.user_data['patient_id']
    vital_sign = context.user_data['current_vital']
    
    try:
        value = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number. Try again:")
        return ENTER_VITAL_SIGN_VALUE
    
    # Check ranges
    param_info = PARAMETER_RANGES.get(vital_sign, {})
    out_of_range = False
    warning = ""
    
    if 'min' in param_info and value < param_info['min']:
        out_of_range = True
        warning = f"⚠️ Below minimum ({param_info['min']}{param_info['unit']})"
    elif 'max' in param_info and value > param_info['max']:
        out_of_range = True
        warning = f"⚠️ Above maximum ({param_info['max']}{param_info['unit']})"
    
    # Save record
    record = {
        "type": "vital_sign",
        "parameter": vital_sign,
        "value": value,
        "unit": param_info.get('unit', ''),
        "timestamp": datetime.now().isoformat(),
        "out_of_range": out_of_range
    }
    save_patient_record(user_id, record)
    
    # Respond to patient
    response = f"✅ Recorded {vital_sign.replace('_', ' ')}: {value}{param_info.get('unit', '')}"
    if out_of_range:
        response += f"\n{warning}\nA doctor has been notified."
        await alert_doctor(context, user_id, vital_sign, value, param_info)
    
    await update.message.reply_text(
        response,
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
    )
    return MAIN_MENU

# ======================
# 2. pain
def pain_location_menu_keyboard():
    return [
        [InlineKeyboardButton("Surgery Site", callback_data='surgery_site')],
        [InlineKeyboardButton("Outside Surgery site", callback_data='outside_surgery_site')],
        [InlineKeyboardButton("Chest", callback_data='chest')],
        [InlineKeyboardButton("Leg", callback_data='leg')],
        [InlineKeyboardButton("Anterior Chest", callback_data='anterior_chest')],
        [InlineKeyboardButton("Arm", callback_data='arm')],
        [InlineKeyboardButton("Back", callback_data='back')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

def anterior_chest_menu_keyboard():
    return [
        [InlineKeyboardButton("Fixed/Continuous", callback_data='fixed_continuous')],
        [InlineKeyboardButton("Stabbing", callback_data='stabbing')],
        [InlineKeyboardButton("Pulsating", callback_data='pulsating')],
        [InlineKeyboardButton("Unlike the previous ones", callback_data='unlike_previous_ones')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

def pain_back_menu_keyboard():
    return [
        [InlineKeyboardButton("Fixed/Continuous", callback_data='fixed_continuous')],
        [InlineKeyboardButton("Stabbing", callback_data='stabbing')],
        [InlineKeyboardButton("Related to movement", callback_data='related_to_movement')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

def pain_type_menu_keyboard():
    return [
        [InlineKeyboardButton("Enter pain type", callback_data='enter_pain_type')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

async def enter_pain_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process pain score ( 0 - 10 )."""
    try:
        # Convert to integer and validate range
        score = int(update.message.text)
        if score < 0 or score > 10:
            raise ValueError("Score out of range")
            
    except ValueError:
        # Invalid input (not a number or out of range)
        await update.message.reply_text(
            "⚠️ Please enter a valid pain score between 0 and 10:",
            reply_markup=InlineKeyboardMarkup(back_only_keyboard('main'))
        )
        return ENTER_PAIN_SCORE  # Stay in same state to retry
    context.user_data['pain_score'] = score
    # Sub-menu for each location
    await update.message.reply_text(
        f"Recorded pain location: {score}\n"
            "Now, Where is your pain located in your body?",
            reply_markup=InlineKeyboardMarkup(pain_location_menu_keyboard())
        )
    return ENTER_PAIN_LOCATION

async def enter_pain_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process pain location input."""
    query = update.callback_query
    await query.answer()
    pain_location = query.data
    context.user_data['pain_location'] = pain_location
    if query.data == 'back_to_main':
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU
    elif query.data == 'anterior_chest':
        await query.edit_message_text(
            f"Recorded pain location: {pain_location}\n"
            "Now please describe the type of pain:",
            reply_markup=InlineKeyboardMarkup(anterior_chest_menu_keyboard())
        )
        return ENTER_PAIN_TYPE
    elif query.data == 'back':
        await query.edit_message_text(
            f"Recorded pain location: {pain_location}\n"
            "Now please describe the type of pain:",
            reply_markup=InlineKeyboardMarkup(pain_back_menu_keyboard())
        )
        return ENTER_PAIN_TYPE
    else:
        await query.edit_message_text(
            f"Recorded pain location: {pain_location}\n",
            reply_markup=InlineKeyboardMarkup(pain_type_menu_keyboard())
        )
        return ENTER_PAIN_TYPE

async def enter_pain_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process pain type input."""
    query = update.callback_query
    await query.answer()
    pain_type = query.data
    context.user_data['pain_type'] = pain_type
    
    await query.edit_message_text(
        f"Recorded pain type: {pain_type}\n"
        "Now, Please describe any symptoms accompanying the pain:\n"
        "Or the situation when the pain happened\n"
        "- Shortness of breath\n"
        "- Numbness\n"
        "- Example: 'some shortness of breath'\n"
        "Example: 'when I walk'",
        reply_markup=InlineKeyboardMarkup(back_only_keyboard('pain_menu'))
    )
    return ENTER_PAIN_SYMPTOMS

async def enter_pain_symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Complete pain assessment and save data."""
    symptoms = update.message.text
    user_id = context.user_data['patient_id']
    
    record = {
        "type": "pain_assessment",
        "location": context.user_data['pain_location'],
        "pain_type": context.user_data['pain_type'],
        "symptoms": symptoms,
        "timestamp": datetime.now().isoformat()
    }
    save_patient_record(user_id, record)
    
    await update.message.reply_text(
        "✅ Pain assessment completed:\n"
        f"Location: {record['location']}\n"
        f"Type: {record['pain_type']}\n"
        f"Symptoms: {record['symptoms']}",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
    )
    return MAIN_MENU

# 3. Respiratory System Handlers
def respiratory_menu_keyboard():
    return [
        [InlineKeyboardButton("Superficial breathing", callback_data='superficial_breathing')],
        [InlineKeyboardButton("More than 30 beats/1 min", callback_data='more_30_beats')],
        [InlineKeyboardButton("Can't breadthe", callback_data='no_breadthe')],
        [InlineKeyboardButton("Accompanied by impaired consciousness", callback_data='impaired_consciousness')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]
# 4. Gastrointestinal Handlers
def gastrointestinal_menu_keyboard():
    return [
        [InlineKeyboardButton("Constipation", callback_data='constipation')],
        [InlineKeyboardButton("Diarrhea", callback_data='diarrhea')],
        [InlineKeyboardButton("Accompanied by (< 70) systolic blood pressure", callback_data='systolic_blood_pressure')],
        [InlineKeyboardButton("Fever (>37.5)", callback_data='fever')],
        [InlineKeyboardButton("No appetite", callback_data='no_appetite')],
        [InlineKeyboardButton("Too weak", callback_data='too_weak')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

# 5. Consciousness Handlers
async def handle_consciousness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process consciousness information."""
    consciousness_level = update.message.text
    context.user_data['consciousness_level'] = consciousness_level

    user_id = context.user_data['patient_id']
    text = consciousness_level.lower()
    
    record = {
        "type": "consciousness",
        "description": text,
        "timestamp": datetime.now().isoformat()
    }
    
    # Check for warning signs from your doc
    warning_signs = ["confused", "disoriented", "unresponsive"]
    if any(sign in text for sign in warning_signs):
        record["needs_attention"] = True
        await alert_doctor(context, user_id, "consciousness", text, {})
    
    save_patient_record(user_id, record)
    
    await update.message.reply_text(
        "✅ Consciousness assessment recorded",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
    )
    return MAIN_MENU

# 6. Emotional Status
# Emotional Status Questionnaire (Beck Anxiety Inventory)
EMOTIONAL_QUESTIONS = [
    "1. Numbness or tingling",
    "2. Feeling hot",
    "3. Wobbliness in legs",
    "4. Unable to relax",
    "5. Fear of worst happening",
    "6. Dizzy or lightheaded",
    "7. Heart pounding/racing",
    "8. Unsteady",
    "9. Terrified or afraid",
    "10. Nervous",
    "11. Feeling of choking",
    "12. Hands trembling",
    "13. Shaky/unsteady",
    "14. Fear of losing control",
    "15. Difficulty breathing",
    "16. Fear of dying",
    "17. Scared",
    "18. Indigestion",
    "19. Faint/lightheaded",
    "20. Face flushed",
    "21. Hot/cold sweats"
]

def emotional_status_keyboard():
    """Create response keyboard for each question"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Not at all (0)", callback_data='0'),
            InlineKeyboardButton("Mildly (1)", callback_data='1')
        ],
        [
            InlineKeyboardButton("Moderately (2)", callback_data='2'),
            InlineKeyboardButton("Severely (3)", callback_data='3')
        ],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')]
    ])

async def start_emotional_assessment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start emotional status assessment"""
    
    # Initialize assessment data
    context.user_data['emotional_assessment'] = {
        'current_question': 0,
        'answers': [],
        'start_time': datetime.now().isoformat()
    }
    
    # Ask first question
    await update.message.reply_text(
        text="Emotional Status Assessment (Beck Anxiety Inventory)\n\n"
             f"{EMOTIONAL_QUESTIONS[0]}\n"
             "How much has this bothered you in the past week?",
        reply_markup=emotional_status_keyboard()
    )
    return ENTER_EMOTIONAL_STATUS

async def handle_emotional_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process response to emotional status questions"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_main':
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU
    
    # Store the answer
    assessment = context.user_data['emotional_assessment']
    assessment['answers'].append(int(query.data))
    current_q = assessment['current_question'] + 1
    
    if current_q < len(EMOTIONAL_QUESTIONS):
        # Ask next question
        assessment['current_question'] = current_q
        await query.edit_message_text(
            text=f"{EMOTIONAL_QUESTIONS[current_q]}\n"
                 "How much has this bothered you in the past week?",
            reply_markup=emotional_status_keyboard()
        )
        return ENTER_EMOTIONAL_STATUS
    else:
        # Assessment complete
        total_score = sum(assessment['answers'])
        assessment['total_score'] = total_score
        assessment['end_time'] = datetime.now().isoformat()
        
        # Interpret score
        if total_score <= 7:
            interpretation = "Minimal anxiety"
        elif total_score <= 15:
            interpretation = "Mild anxiety"
        elif total_score <= 25:
            interpretation = "Moderate anxiety"
        else:
            interpretation = "Severe anxiety"
        
        # Save results
        user_id = context.user_data['patient_id']
        record = {
            "type": "emotional_assessment",
            "assessment": "Beck Anxiety Inventory",
            "score": total_score,
            "interpretation": interpretation,
            "answers": assessment['answers'],
            "timestamp": assessment['start_time'],
            "duration_seconds": (datetime.now() - datetime.fromisoformat(assessment['start_time'])).total_seconds()
        }
        save_patient_record(user_id, record)
        
        # Alert doctor if score is concerning
        if total_score > 15:
            await alert_doctor(
                context,
                user_id,
                "emotional_status",
                f"Score: {total_score} ({interpretation})",
                {}
            )
        
        await query.edit_message_text(
            text=f"✅ Emotional assessment completed\n\n"
                 f"Total score: {total_score}\n"
                 f"Interpretation: {interpretation}",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
            
        )
        return MAIN_MENU
    
# 7. Compliance with medications
# 9. Adaptation to post operation rehabilitation
# 10. Using of stocking socks
# 11. Compliance with diet
# 12. Gradual adaptation to activity
# 13. Adaptation to daily mobilization
# 14. Adating to social life
# 15. Shower
# 16. Back to job
# 17. Driving

async def handle_problem_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the problem menu."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_main':
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU
    
    if query.data == 'no_problem':
        await query.edit_message_text(
            f"✅ No problem with {context.user_data['current_parameter']}, Main Menu:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU
    elif query.data == 'problem':
        await query.edit_message_text(
        "Now, Please describe any difficulties or the problem.\n",
        reply_markup=InlineKeyboardMarkup(back_only_keyboard('menu'))
        )
        return ENTER_PROBLEM_DESCRIPTION
    
async def enter_problem_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process problem information."""
    user_id = context.user_data['patient_id']
    text = update.message.text
    current_parameter = context.user_data['current_parameter']
    print(current_parameter)
    await alert_doctor(context, user_id, current_parameter, text, {})
    
    record = {
        "type": current_parameter,
        "description": text,
        "timestamp": datetime.now().isoformat()
    }
    
    save_patient_record(user_id, record)
    
    await update.message.reply_text(
        "✅ Problem recorded",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
    )
    return MAIN_MENU

# 8. Wound Healing Handlers
def wound_healing_menu_keyboard():
    return [
        [InlineKeyboardButton("Wound dranaige", callback_data='wound_dranaige')],
        [InlineKeyboardButton("Increased redness at the wound site", callback_data='increased_redness')],
        [InlineKeyboardButton("Color changed at the wound site", callback_data='color_changed')],
        [InlineKeyboardButton("Fever", callback_data='fever')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

async def enter_wound_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle wound healing assessment."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_main':
        await main_menu(query)
        return MAIN_MENU
    
    user_id = context.user_data['patient_id']
    text = query.data.lower()
    
    record = {
        "type": "wound_assessment",
        "description": text,
        "timestamp": datetime.now().isoformat()
    }
    save_patient_record(user_id, record)

    # Check for warning signs from your doc
    warning_signs = ["increased_redness", "color_changed", "fever"]
    if any(sign in text for sign in warning_signs):
        record["needs_attention"] = True
        await alert_doctor(context, user_id, "wound_status", text, {})
    
    
    await query.edit_message_text(
        "✅ Wound assessment recorded",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
    )
    return MAIN_MENU
    
# 18. & 19. Sleep Pattern and Position Handlers
def sleep_pattern_menu_keyboard():
    return [
        [InlineKeyboardButton("Falling asleep", callback_data='falling_asleep')],
        [InlineKeyboardButton("Shorter sleep time", callback_data='short_time')],
        [InlineKeyboardButton("Feeling tired when waking up", callback_data='feeling_tired')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

def sleep_position_menu_keyboard():
    return [
        [InlineKeyboardButton("On the back", callback_data='back')],
        [InlineKeyboardButton("Side sleeping", callback_data='side')],
        [InlineKeyboardButton("Use of two pillows", callback_data='two_pillows')],
        [InlineKeyboardButton("Orthopnea", callback_data='orthopnea')],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')],
    ]

# 20. Postoperative quality of recovery

# Quality of Recovery (QoR-15) Questionnaire
QOR_QUESTIONS = [
    "1. Able to breathe easily",
    "2. Been able to enjoy food",
    "3. Feeling rested",
    "4. Have had a good sleep",
    "5. Able to look after personal toilet and hygiene unaided",
    "6. Able to communicate with family or friends",
    "7. Getting support from hospital doctors and nurses",
    "8. Able to return to work or usual home activities",
    "9. Feeling comfortable and in control",
    "10. Having a feeling of general well-being",
    "11. Having moderate pain",
    "12. Severe pain",
    "13. Nausea or vomiting",
    "14. Feeling worried or anxious",
    "15. Feeling sad or depressed"
]

# QoR response options (0-10 scale)
def qor_response_keyboard():
    """Create response keyboard for QoR questions"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("0 = none of the time (Poor)", callback_data='0')
        ],
        [
            InlineKeyboardButton("1", callback_data='1'),
            InlineKeyboardButton("2", callback_data='2'),
            InlineKeyboardButton("3", callback_data='3')
        ],
        [
            InlineKeyboardButton("4", callback_data='4'),
            InlineKeyboardButton("5", callback_data='5'),
            InlineKeyboardButton("6", callback_data='6'),
        ],
        [
            InlineKeyboardButton("7", callback_data='7'),
            InlineKeyboardButton("8", callback_data='8'),
            InlineKeyboardButton("9", callback_data='9')
        ],
        [
            InlineKeyboardButton("10 = all of the time (Excellent)", callback_data='10')
        ],
        [InlineKeyboardButton("◀ Back to Main Menu", callback_data='back_to_main')]
    ])

async def start_qor_assessment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start Postoperative Quality of Recovery assessment"""
    
    # Initialize assessment data
    context.user_data['qor_assessment'] = {
        'current_question': 0,
        'answers': [],
        'start_time': datetime.now().isoformat()
    }
    
    # Ask first question
    await update.message.reply_text(
        text="Postoperative Quality of Recovery (QoR-15)\n\n"
             "Please rate your recovery experience (0 = worst, 10 = best)\n\n"
             f"{QOR_QUESTIONS[0]}",
        reply_markup=qor_response_keyboard()
    )
    return ENTER_QOR_RESPONSE

async def handle_qor_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process response to QoR questions"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_main':
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU
    
    # Store the answer (0-10 scale)
    assessment = context.user_data['qor_assessment']
    assessment['answers'].append(int(query.data))
    current_q = assessment['current_question'] + 1
    
    if current_q < len(QOR_QUESTIONS):
        # Ask next question
        assessment['current_question'] = current_q
        question_text = QOR_QUESTIONS[current_q]
        
        # Adjust instructions for pain questions (11-12)
        instructions = "Please rate your pain (0 = no pain, 10 = worst imaginable)" \
            if current_q in [10, 11] else "Please rate your recovery (0 = worst, 10 = best)"
        
        await query.edit_message_text(
            text=f"Postoperative Quality of Recovery (QoR-15)\n\n"
                 f"{instructions}\n\n"
                 f"{question_text}",
            reply_markup=qor_response_keyboard()
        )
        return ENTER_QOR_RESPONSE
    else:
        # Assessment complete - calculate scores
        total_score = sum(assessment['answers'][:10]) +(20 - sum(assessment['answers'][10:13])) +(20 - sum(assessment['answers'][13:15]))
        
        assessment['total_score'] = total_score
        assessment['end_time'] = datetime.now().isoformat()
        
        # Interpretation (QoR-15 ranges: 0-30 poor, 31-80 moderate, 81-150 good)
        if total_score <= 30:
            interpretation = "Poor recovery"
        elif total_score <= 80:
            interpretation = "Moderate recovery"
        else:
            interpretation = "Good recovery"
        
        # Save results
        user_id = context.user_data['patient_id']
        record = {
            "type": "qor_assessment",
            "assessment": "QoR-15",
            "score": total_score,
            "interpretation": interpretation,
            "answers": assessment['answers'],
            "timestamp": assessment['start_time'],
            "duration_seconds": (datetime.now() - datetime.fromisoformat(assessment['start_time'])).total_seconds()
        }
        save_patient_record(user_id, record)
        
        # Alert doctor if poor recovery
        if total_score <= 80:
            await alert_doctor(
                context,
                user_id,
                "postop_recovery",
                f"QoR-15 Score: {total_score} ({interpretation})",
                {}
            )
        
        await query.edit_message_text(
            text=f"✅ Postoperative Recovery Assessment Completed\n\n"
                 f"Total QoR-15 score: {total_score}/150\n"
                 f"Interpretation: {interpretation}\n\n"
                 "Scores:\n"
                 f"- Physical comfort: {sum(assessment['answers'][:5])/5.0:.1f}/10\n"
                 f"- Emotional state: {sum(assessment['answers'][13:15])/2.0:.1f}/10\n"
                 f"- Pain control: {sum(assessment['answers'][10:12])/2.0:.1f}/10",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
            
        )
        return MAIN_MENU

# ======================
# HELPER FUNCTIONS
# ======================
async def handle_submenu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle sub-menu assessment."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back_to_main':
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU
    else:
        user_id = context.user_data['patient_id']
        text = query.data
        current_parameter = context.user_data['current_parameter']
        print(current_parameter)
        await alert_doctor(context, user_id, current_parameter, text, {})
        
        record = {
            "type": current_parameter,
            "description": text,
            "timestamp": datetime.now().isoformat()
        }
        
        save_patient_record(user_id, record)
        
        await query.edit_message_text(
            "✅ Problem recorded",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
        )
        return MAIN_MENU

def save_patient_record(user_id: int, record: dict):
    """Save patient record to JSON file."""
    filename = os.path.join(DATA_DIR, f"patient_{user_id}.json")
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        data = {"records": []}
    
    data['records'].append(record)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

async def alert_doctor(context: ContextTypes.DEFAULT_TYPE, patient_id: int, 
                     parameter: str, value: float, param_info: dict):
    """Send alert to doctor about out-of-range value."""
    message = (
        f"🚨 PATIENT ALERT\n"
        f"Patient ID: {patient_id}\n"
        f"Parameter: {parameter.replace('_', ' ')}\n"
        f"Value: {value}{param_info.get('unit', '')} "
    )
    #print(param_info)
    if param_info:
        if 'min' in param_info and value < param_info['min']:
            message += f"(below minimum of {param_info['min']}{param_info['unit']})"
        else:
            message += f"(above maximum of {param_info['max']}{param_info['unit']})"
        
    await context.bot.send_message(chat_id=DOCTOR1_CHAT_ID, text=message)
    await context.bot.send_message(chat_id=DOCTOR2_CHAT_ID, text=message)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard())
    )
    return MAIN_MENU

# ======================
# BOT SETUP
# ======================

def main():
    """Run the bot."""
    application = Application.builder().token("7858545951:AAGW9ErUT7bkm04AZj13V18nfe1d1tFAJQM").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(main_menu, pattern='^(vital_signs|pain|respiratory|gastrointestinal|consciousness|emotional_status|medication_compliance|wound_healing|postop_adaptation|stocking_socks|diet_compliance|activity_adaptation|daily_mobilization|social_adaptation|shower|return_to_work|driving|sleep_pattern|sleep_position|postoperative_quality_of_recovery)$')
            ],
            
            VITAL_SIGNS_MENU: [
                CallbackQueryHandler(vital_signs_menu, pattern='^(heart_rate|systolic_blood_pressure|diastolic_blood_pressure|respiration_rate|temperature|back_to_main)$')
            ],
            ENTER_VITAL_SIGN_VALUE: [
                MessageHandler(TEXT & ~COMMAND, enter_vital_sign_value)
            ],
            ENTER_PAIN_SCORE: [
                MessageHandler(TEXT & ~COMMAND, enter_pain_score)
            ],
            ENTER_PAIN_LOCATION: [
                CallbackQueryHandler(enter_pain_location, pattern='^(surgery_site|outside_surgery_site|chest|leg|anterior_chest|arm|back|back_to_main)$')
            ],
            ENTER_PAIN_TYPE: [
                CallbackQueryHandler(enter_pain_type, pattern='^(fixed_continuous|stabbing|pulsating|related_to_movement|unlike_previous_ones|enter_pain_type|back_to_main)$')
            ],
            ENTER_PAIN_SYMPTOMS: [
                MessageHandler(TEXT & ~COMMAND, enter_pain_symptoms)
            ],
            
            RESPIRATORY_SYSTEM: [
                CallbackQueryHandler(handle_submenu, pattern='^(superficial_breathing|more_30_beats|no_breadthe|impaired_consciousness|back_to_main)$')
            ],
            
            GASTROINTESTINAL_SYSTEM: [
                CallbackQueryHandler(handle_submenu, pattern='^(constipation|diarrhea|systolic_blood_pressure|fever|no_appetite|too_weak|back_to_main)$')
            ],

            CONSCIOUSNESS: [
                MessageHandler(TEXT & ~COMMAND, handle_consciousness)
            ],

            EMOTIONAL_STATUS_MENU: [
                MessageHandler(TEXT & ~COMMAND, start_emotional_assessment)
            ],
            ENTER_EMOTIONAL_STATUS: [
                CallbackQueryHandler(handle_emotional_response)
            ],
            
            PROBLEM_MENU: [
                CallbackQueryHandler(handle_problem_menu, pattern='^(no_problem|problem|back_to_main)$')
            ],

            ENTER_PROBLEM_DESCRIPTION: [
                MessageHandler(TEXT & ~COMMAND, enter_problem_info)
            ],

            WOUND_HEALING_MENU: [
                CallbackQueryHandler(enter_wound_info, pattern='^(wound_dranaige|increased_redness|color_changed|fever|back_to_main)$')
            ],
            
            SLEEP_PATTERN: [
                CallbackQueryHandler(handle_submenu, pattern='^(falling_asleep|short_time|feeling_tired|back_to_main)$')
            ],

            SLEEP_POSITION: [
                CallbackQueryHandler(handle_submenu, pattern='^(back|side|two_pillows|orthopnea|back_to_main)$')
            ],

            QOR_ASSESSMENT_MENU: [
                MessageHandler(TEXT & ~COMMAND, start_qor_assessment)
            ],
            ENTER_QOR_RESPONSE: [
                CallbackQueryHandler(handle_qor_response)
            ],
            
            DOCTOR_ALERT: [
                CallbackQueryHandler(alert_doctor, pattern='^(acknowledged|follow_up)$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    
    application.add_handler(conv_handler)
    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))
    application.run_polling()

if __name__ == '__main__':
    main()