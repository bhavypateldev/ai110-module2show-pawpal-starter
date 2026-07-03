"""PawPal+ Streamlit UI.

This is the presentation layer. All the real logic lives in pawpal_system.py;
this file just imports those classes, keeps a single Owner in session state, and
wires the buttons/forms to the methods built in Phase 2.
"""

from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Application memory -------------------------------------------------------
# Streamlit re-runs this whole script on every interaction, so we stash the
# Owner in st.session_state. It is created once and reused on later reruns,
# which keeps pets and tasks from being wiped out each time the page refreshes.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=90)
owner: Owner = st.session_state.owner

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. Add an owner and pets, give each pet
some care tasks (with a duration and priority), then generate a daily plan that
fits your available time and explains its choices.
"""
    )

# --- Owner --------------------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input(
        "Daily time available (minutes)",
        min_value=5,
        max_value=600,
        value=owner.available_minutes,
        step=5,
        help="The total time budget the scheduler must fit tasks into.",
    )
)

# --- Add a pet ----------------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        breed = st.text_input("Breed")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species, breed=breed.strip()))
            st.success(f"Added {pet_name.strip()}.")
        else:
            st.warning("Please enter a pet name.")

if not owner.pets:
    st.info("No pets yet. Add one above to start planning.")

# --- Add a task ---------------------------------------------------------------
if owner.pets:
    st.subheader("Tasks")
    # Select the target pet by index so pets with the same name don't collide.
    target_index = st.selectbox(
        "Add task to",
        options=list(range(len(owner.pets))),
        format_func=lambda i: owner.pets[i].name,
    )

    with st.form("add_task_form", clear_on_submit=True):
        row1 = st.columns(3)
        with row1[0]:
            title = st.text_input("Task title", value="Morning walk")
        with row1[1]:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with row1[2]:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        row2 = st.columns(3)
        with row2[0]:
            category = st.text_input("Category", value="general")
        with row2[1]:
            preferred_time = st.text_input("Preferred time (HH:MM)", value="")
        with row2[2]:
            frequency = st.selectbox("Repeats", ["none", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            pet = owner.pets[target_index]
            pet.add_task(
                Task(
                    title=title.strip() or "Untitled task",
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category.strip() or "general",
                    preferred_time=preferred_time.strip() or None,
                    frequency=frequency,
                    due_date=date.today() if frequency != "none" else None,
                )
            )
            st.success(f"Added '{title.strip() or 'Untitled task'}' to {pet.name}.")

    # --- Show current pets and tasks (with a done toggle) ---------------------
    st.markdown("### Current pets & tasks")
    for pet_i, pet in enumerate(owner.pets):
        label = f"**{pet.name}** — {pet.species}"
        if pet.breed:
            label += f" ({pet.breed})"
        st.markdown(label)
        if not pet.tasks:
            st.caption("No tasks yet.")
        for task_i, task in enumerate(pet.tasks):
            check_col, text_col = st.columns([0.12, 0.88])
            with check_col:
                done = st.checkbox(
                    "done",
                    value=task.completed,
                    key=f"done_{pet_i}_{task_i}",
                    label_visibility="collapsed",
                )
            with text_col:
                when = f" @ {task.preferred_time}" if task.preferred_time else ""
                repeats = f" · repeats {task.frequency}" if task.is_recurring() else ""
                st.write(
                    f"{task.title} — {task.duration_minutes} min "
                    f"[{task.priority}]{when}{repeats}"
                )
            # Reflect the checkbox back onto the Task object.
            if done:
                task.mark_complete()
            else:
                task.mark_incomplete()

# --- Build schedule -----------------------------------------------------------
st.divider()
st.subheader("Build schedule")
st.caption("Generates a daily plan from all pending tasks, ordered by priority.")

if st.button("Generate schedule"):
    scheduler = Scheduler(available_minutes=owner.available_minutes, day_start="08:00")
    plan = scheduler.build_plan(owner.all_tasks())

    if not plan:
        st.warning(
            "Nothing to schedule. Add some tasks — or they may all be completed "
            "or too long to fit the available time."
        )
    else:
        def pet_of(task: Task) -> str:
            """Return the name of the pet that owns this task (identity match)."""
            for pet in owner.pets:
                if any(task is t for t in pet.tasks):
                    return pet.name
            return "?"

        st.table(
            [
                {
                    "Start": item.start_time,
                    "Task": item.task.title,
                    "Pet": pet_of(item.task),
                    "Duration (min)": item.task.duration_minutes,
                    "Priority": item.task.priority,
                }
                for item in plan
            ]
        )
        with st.expander("Why this plan?", expanded=True):
            st.text(scheduler.explain(plan))
