from datetime import datetime, timedelta
from backend.models import (
    Participant, Problem, Submission, Contest, Result,
    get_session, init_db
)
from backend.problem_loader import load_all_problems, get_problem_with_starter_code
from backend.judge import Judge
import config
from firebase_config import get_db, firestore

class ContestService:
    """Service layer for contest management"""
    
    def __init__(self):
        init_db()
        self.judge = Judge()
    
    def register_participant(self, name, email, language):
        """Register a new participant or resume existing session"""
        session = get_session()
        try:
            # Check for existing participant by email
            existing_participant = session.query(Participant).filter_by(email=email).first()
            
            if existing_participant:
                # Check their contest status
                contest = session.query(Contest).filter_by(participant_id=existing_participant.id).first()
                if contest:
                    if contest.status in ['COMPLETED', 'DISQUALIFIED']:
                        session.close()
                        raise Exception("You have already completed the test. Duplicate entries are not allowed.")
                    elif contest.is_active:
                        # Allow resuming active session
                        # Update name/language preferences if changed? preferably not to keep consistency
                        p_id = existing_participant.id
                        session.close()
                        return p_id
            
            # New participant
            participant = Participant(name=name, email=email, language=language.lower())
            session.add(participant)
            session.commit()
            participant_id = participant.id
            session.close()
            return participant_id
        except Exception as e:
            session.rollback()
            session.close()
            raise e
    
    def get_participant(self, participant_id):
        """Get participant details"""
        session = get_session()
        participant = session.query(Participant).filter_by(id=participant_id).first()
        session.close()
        
        if participant:
            return {'id': participant.id, 'name': participant.name, 'email': participant.email, 'language': participant.language}
        return None
    
    def start_contest(self, participant_id):
        """Start contest for a participant"""
        session = get_session()
        try:
            existing = session.query(Contest).filter_by(participant_id=participant_id).first()
            if existing:
                if existing.status == 'DISQUALIFIED':
                    session.close()
                    return False, "You have been disqualified from the contest."
                if existing.is_active == 0:
                     session.close()
                     return False, "Contest already completed"
                
                session.close()
                return False, "Contest already started"
            
            contest = Contest(
                participant_id=participant_id, 
                start_time=datetime.now(), 
                duration=config.CONTEST_DURATION, 
                is_active=1,
                status='ACTIVE',
                violation_count=0
            )
            session.add(contest)
            session.commit()
            session.close()
            return True, "Contest started"
        except Exception as e:
            session.rollback()
            session.close()
            return False, str(e)
    
    def get_contest_status(self, participant_id):
        """Get contest status and remaining time"""
        session = get_session()
        contest = session.query(Contest).filter_by(participant_id=participant_id).first()
        session.close()
        
        if not contest:
            return None
        
        if not contest.is_active:
            return {'is_active': False, 'remaining_time': 0, 'elapsed_time': contest.duration}
        
        elapsed = (datetime.now() - contest.start_time).total_seconds()
        remaining = max(0, contest.duration - elapsed)
        
        if remaining == 0:
            self.end_contest(participant_id)
        
        return {
            'is_active': contest.is_active == 1, 
            'remaining_time': int(remaining), 
            'elapsed_time': int(elapsed), 
            'start_time': contest.start_time.isoformat(),
            'violation_count': contest.violation_count,
            'status': contest.status
        }
    
    def end_contest(self, participant_id):
        """End contest and calculate final results"""
        session = get_session()
        try:
            contest = session.query(Contest).filter_by(participant_id=participant_id).first()
            if contest:
                contest.is_active = 0
                contest.end_time = datetime.now()
                if contest.status == 'ACTIVE':
                    contest.status = 'COMPLETED'
                session.commit()
            
            self._calculate_results(participant_id, session)
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            return False
    
    def get_all_problems(self):
        """Get all problems without test cases"""
        return load_all_problems()
    
    def get_problem(self, problem_id, language):
        """Get problem with starter code"""
        return get_problem_with_starter_code(problem_id, language)
    
    def submit_code(self, participant_id, problem_id, code, language):
        """Submit code for judging"""
        session = get_session()
        
        try:
            contest_status = self.get_contest_status(participant_id)
            if not contest_status or not contest_status['is_active']:
                session.close()
                return {'success': False, 'message': 'Contest is not active', 'verdict': None, 'score': 0}
            
            verdict, score, details = self.judge.judge_submission(problem_id, code, language)
            
            submission = Submission(participant_id=participant_id, problem_id=problem_id, code=code, language=language, verdict=verdict, score=score)
            session.add(submission)
            
            # Update total score immediately
            self._calculate_results(participant_id, session)
            
            session.commit()
            
            submission_id = submission.id
            session.close()
            
            return {'success': True, 'submission_id': submission_id, 'verdict': verdict, 'score': score, 'details': details}
        except Exception as e:
            session.rollback()
            session.close()
            return {'success': False, 'message': str(e), 'verdict': 'Error', 'score': 0}
    
    def get_submissions(self, participant_id):
        """Get all submissions for a participant"""
        session = get_session()
        submissions = session.query(Submission).filter_by(participant_id=participant_id).all()
        
        result = []
        for sub in submissions:
            result.append({'id': sub.id, 'problem_id': sub.problem_id, 'verdict': sub.verdict, 'score': sub.score, 'submitted_at': sub.submitted_at.isoformat()})
        
        session.close()
        return result
    
    def get_results(self, participant_id):
        """Get final results for a participant"""
        session = get_session()
        result = session.query(Result).filter_by(participant_id=participant_id).first()
        
        if not result:
            self._calculate_results(participant_id, session)
            session.commit()
            result = session.query(Result).filter_by(participant_id=participant_id).first()
        
        if result:
            output = {'participant_id': result.participant_id, 'total_score': result.total_score, 'problems_solved': result.problems_solved, 'performance_level': result.performance_level}
            session.close()
            return output
        
        session.close()
        return None
    
    def _calculate_results(self, participant_id, session):
        """Calculate and save final results with relative ranking"""
        submissions = session.query(Submission).filter_by(participant_id=participant_id).all()
        
        problem_scores = {}
        for sub in submissions:
            if sub.problem_id not in problem_scores:
                problem_scores[sub.problem_id] = sub.score
            else:
                problem_scores[sub.problem_id] = max(problem_scores[sub.problem_id], sub.score)
        
        total_score = sum(problem_scores.values())
        problems_solved = sum(1 for score in problem_scores.values() if score == config.MARKS_PER_PROBLEM)
        
        # Calculate rank among all participants
        all_results = session.query(Result).all()
        scores_list = [(r.participant_id, r.total_score) for r in all_results if r.participant_id != participant_id]
        scores_list.append((participant_id, total_score))
        
        # Sort by score descending
        scores_list.sort(key=lambda x: x[1], reverse=True)
        
        # Find rank (1-indexed)
        rank = next(i + 1 for i, (pid, _) in enumerate(scores_list) if pid == participant_id)
        total_participants = len(scores_list)
        
        # Get performance level based on rank
        performance_level = config.get_performance_level(rank, total_participants)
        
        # Save or update result
        result = session.query(Result).filter_by(participant_id=participant_id).first()
        if result:
            result.total_score = total_score
            result.problems_solved = problems_solved
            result.performance_level = performance_level
        else:
            result = Result(participant_id=participant_id, total_score=total_score, problems_solved=problems_solved, performance_level=performance_level)
            session.add(result)

    def record_violation(self, participant_id):
        """Record an anti-cheating violation"""
        session = get_session()
        try:
            contest = session.query(Contest).filter_by(participant_id=participant_id).first()
            if not contest or not contest.is_active:
                session.close()
                return {'success': False, 'message': 'No active contest'}
            
            contest.violation_count += 1
            current_count = contest.violation_count
            
            status = 'ACTIVE'
            if current_count >= 3:
                contest.status = 'DISQUALIFIED'
                contest.is_active = 0
                status = 'DISQUALIFIED'
                
            session.commit()
            session.close()
            return {'success': True, 'violation_count': current_count, 'status': status}
        except Exception as e:
            session.rollback()
            session.close()
            return {'success': False, 'message': str(e)}

    def get_leaderboard_data(self):
        """Get data for organizer leaderboard with auto-finalization of expired sessions"""
        session = get_session()
        
        # 1. Lazy Finalization of expired sessions
        try:
            active_contests = session.query(Contest).filter_by(status='ACTIVE').all()
            if active_contests:
                db = get_db()
                for contest in active_contests:
                    if contest.start_time:
                        # Ensure comparison is timezone-naive or consistent
                        now = datetime.now()
                        st = contest.start_time
                        
                        # Strip timezone if present to avoid comparison errors
                        if st.tzinfo is not None: st = st.replace(tzinfo=None)
                        if now.tzinfo is not None: now = now.replace(tzinfo=None)
                        
                        elapsed = (now - st).total_seconds()
                        
                        # If more than 2 hours passed, or if time is negative (timezone glitch), finalize
                        if elapsed >= contest.duration or elapsed < -3600:
                            # Finalize and cap the time at max duration
                            contest.is_active = 0
                            contest.status = 'COMPLETED'
                            capped_end_time = contest.start_time + timedelta(seconds=contest.duration)
                            contest.end_time = capped_end_time
                            
                            # SYNCHRONIZE WITH FIRESTORE (Stop the live timer in organizer.html)
                            if db:
                                try:
                                    # Participant IDs are strings in Firestore
                                    p_ref = db.collection('participants').document(str(contest.participant_id))
                                    p_ref.update({
                                        'status': 'COMPLETED',
                                        'end_time': capped_end_time
                                    })
                                    print(f"Synced finalization to Firestore for participant {contest.participant_id}")
                                except Exception as fe:
                                    print(f"Firestore sync failed for {contest.participant_id}: {fe}")

                            print(f"Auto-finalized session for participant {contest.participant_id}")
            
            session.commit()
        except Exception as e:
            print(f"Error during auto-finalization: {e}")
            session.rollback()

        # 2. Fetch data for leaderboard
        participants = session.query(Participant).all()
        results = session.query(Result).all()
        contests = session.query(Contest).all()
        
        res_map = {r.participant_id: r for r in results}
        con_map = {c.participant_id: c for c in contests}
        
        leaderboard = []
        for p in participants:
            r = res_map.get(p.id)
            c = con_map.get(p.id)
            
            if not c:
                continue # Skip if no contest started
                
            entry = {
                'id': p.id,
                'name': p.name,
                'email': p.email,
                'score': r.total_score if r else 0,
                'solved': r.problems_solved if r else 0,
                'status': c.status,
                'violations': c.violation_count,
                'time_taken': 'N/A'
            }
            
            if c.start_time:
                # Calculate duration
                if c.status == 'COMPLETED' and c.end_time:
                     diff = c.end_time - c.start_time
                elif c.status == 'ACTIVE':
                     diff = datetime.now() - c.start_time
                else:
                     diff = None
                
                if diff:
                    total_seconds = int(diff.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    
                    time_str = ""
                    if hours > 0:
                        time_str += f"{hours}h "
                    if minutes > 0 or hours > 0:
                        time_str += f"{minutes}m "
                    time_str += f"{seconds}s"
                    
                    if c.status == 'ACTIVE':
                        entry['time_taken'] = f"{time_str} (Running)"
                    elif c.status == 'DISQUALIFIED':
                         entry['time_taken'] = "Disqualified"
                    else:
                        entry['time_taken'] = time_str
            
            leaderboard.append(entry)
            
        # Sort by Score (Desc), then Time (Asc)? Or just Score for now.
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1
            
        session.close()
        return leaderboard
