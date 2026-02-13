# Requirements Document: LectureIQ

## Introduction

LectureIQ is an AI-powered learning co-pilot platform designed for engineering and science college students in India. The system converts lecture audio recordings into comprehensive learning materials including structured notes, flashcards, multiple-choice questions, and curated resource links. The platform addresses the challenge of efficient exam preparation and time-saving note-taking for students attending technical lectures delivered in Hindi-English code-mixed language.

## Glossary

- **System**: The LectureIQ platform (backend and frontend combined)
- **Audio_Processor**: Component responsible for transcribing audio files using Whisper
- **Content_Generator**: Component that generates study materials using LLM
- **Resource_Linker**: Component that finds and curates external learning resources
- **Storage_Service**: Component managing file storage on Amazon S3
- **Authentication_Service**: Component handling user authentication via JWT
- **Dashboard**: User interface for viewing lectures and study materials
- **Lecture**: An uploaded audio recording with associated metadata and generated materials
- **Transcript**: Timestamped text output from audio transcription
- **Study_Materials**: Generated notes, flashcards, and MCQs for a lecture
- **User**: A student using the platform
- **Processing_Job**: Asynchronous task for transcribing and generating materials

## Requirements

### Requirement 1: Audio File Upload

**User Story:** As a student, I want to upload lecture audio recordings, so that I can generate study materials from them.

#### Acceptance Criteria

1. WHEN a user drags and drops an audio file onto the upload area, THE System SHALL accept files in MP3, WAV, or M4A format
2. WHEN a user attempts to upload a file larger than 100MB, THE System SHALL reject the upload and display an error message
3. WHEN a valid audio file is uploaded, THE System SHALL store it in the Storage_Service and create a Lecture record
4. WHEN an upload is in progress, THE System SHALL display upload progress percentage to the user
5. WHEN an upload completes successfully, THE System SHALL redirect the user to the processing status page

### Requirement 2: Audio Transcription

**User Story:** As a student, I want my lecture audio to be transcribed accurately, so that I can review the spoken content as text.

#### Acceptance Criteria

1. WHEN a Lecture is created, THE Audio_Processor SHALL transcribe the audio using OpenAI Whisper base model
2. WHEN transcribing audio, THE Audio_Processor SHALL support Hindi, English, and code-mixed Hindi-English language
3. WHEN transcription completes, THE Audio_Processor SHALL generate a Transcript with timestamps for each segment
4. WHEN processing a 1-hour lecture, THE Audio_Processor SHALL complete transcription within 3 minutes
5. IF transcription fails, THEN THE System SHALL mark the Lecture as failed and notify the user with an error message

### Requirement 3: Study Material Generation

**User Story:** As a student, I want AI-generated study materials from my lectures, so that I can efficiently prepare for exams.

#### Acceptance Criteria

1. WHEN a Transcript is available, THE Content_Generator SHALL generate structured notes in markdown format with headers, bullets, and formulas
2. WHEN generating study materials, THE Content_Generator SHALL create 10-15 flashcards in question-answer format per lecture
3. WHEN generating study materials, THE Content_Generator SHALL create 5-10 multiple-choice questions with detailed explanations
4. WHEN processing STEM subject lectures, THE Content_Generator SHALL recognize and format mathematical formulas correctly
5. WHEN generating notes, THE Content_Generator SHALL extract key concepts including definitions, theorems, and algorithms
6. WHEN all study materials are generated, THE System SHALL mark the Lecture as completed and make materials available to the user

### Requirement 4: Resource Discovery and Linking

**User Story:** As a student, I want relevant external resources linked to my lecture topics, so that I can explore concepts in more depth.

#### Acceptance Criteria

1. WHEN study materials are generated, THE Resource_Linker SHALL extract key topics from the Transcript using NLP
2. WHEN topics are extracted, THE Resource_Linker SHALL search for relevant YouTube tutorial videos for each topic
3. WHEN topics relate to programming, THE Resource_Linker SHALL find official documentation links
4. WHEN topics are identified, THE Resource_Linker SHALL suggest practice problems where applicable
5. WHEN displaying resources, THE System SHALL show the top 3-5 most relevant resources per lecture
6. WHEN no relevant resources are found for a topic, THE System SHALL continue processing without failing

### Requirement 5: Learning Dashboard

**User Story:** As a student, I want to view all my uploaded lectures and their materials in one place, so that I can easily access my study content.

#### Acceptance Criteria

1. WHEN a user accesses the Dashboard, THE System SHALL display all Lectures uploaded by that user
2. WHEN displaying Lectures, THE System SHALL show the processing status for each Lecture in real-time
3. WHEN a Lecture is completed, THE Dashboard SHALL provide access to notes, flashcards, and quizzes
4. WHEN a user requests to download materials, THE System SHALL generate and provide a PDF containing all study materials
5. WHEN displaying the Dashboard, THE System SHALL show quiz performance metrics and identified weak areas for each Lecture

### Requirement 6: Interactive Study Tools

**User Story:** As a student, I want interactive flashcard and quiz features, so that I can actively review and test my knowledge.

#### Acceptance Criteria

1. WHEN a user starts flashcard review, THE System SHALL display flashcards one at a time with question on front and answer on back
2. WHEN reviewing flashcards, THE System SHALL implement spaced repetition algorithm to prioritize cards based on user performance
3. WHEN a user takes an MCQ quiz, THE System SHALL display questions one at a time and provide instant feedback on answers
4. WHEN a quiz is completed, THE System SHALL calculate and display the score with detailed explanations for incorrect answers
5. WHEN a user marks a flashcard as difficult, THE System SHALL increase the frequency of that card in future review sessions

### Requirement 7: Pre-Exam Summary Generation

**User Story:** As a student, I want to generate summaries from multiple lectures, so that I can efficiently review before exams.

#### Acceptance Criteria

1. WHEN a user selects multiple Lectures, THE Content_Generator SHALL generate a consolidated summary covering all selected lectures
2. WHEN generating a summary, THE Content_Generator SHALL identify and highlight the most important concepts across lectures
3. WHEN a summary is generated, THE System SHALL organize content by topic rather than by lecture chronology
4. WHEN displaying the summary, THE System SHALL include cross-references to original lecture materials
5. WHEN a user requests a summary, THE System SHALL complete generation within 2 minutes for up to 10 lectures

### Requirement 8: User Authentication and Authorization

**User Story:** As a student, I want secure access to my account, so that my lecture materials remain private.

#### Acceptance Criteria

1. WHEN a new user registers, THE Authentication_Service SHALL create an account with email and password
2. WHEN a user logs in, THE Authentication_Service SHALL issue a JWT token valid for 7 days
3. WHEN a user accesses protected resources, THE System SHALL validate the JWT token before granting access
4. WHEN a JWT token expires, THE System SHALL require the user to log in again
5. WHEN a user logs out, THE System SHALL invalidate the current JWT token
6. WHEN a user attempts to access another user's Lecture, THE System SHALL deny access and return an authorization error

### Requirement 9: Performance and Scalability

**User Story:** As a student, I want fast processing of my lectures, so that I can access study materials quickly.

#### Acceptance Criteria

1. WHEN processing a 1-hour lecture, THE System SHALL complete all processing (transcription and material generation) within 3 minutes
2. WHEN 100 users are accessing the System concurrently, THE System SHALL maintain response times under 2 seconds for API requests
3. WHEN multiple Processing_Jobs are queued, THE System SHALL process them asynchronously without blocking user interactions
4. WHEN the Dashboard loads, THE System SHALL display the lecture list within 1 second
5. WHEN users are on low-bandwidth connections (2G/3G), THE System SHALL load the interface within 5 seconds

### Requirement 10: Data Storage and Management

**User Story:** As a student, I want my audio files and materials stored securely, so that I can access them anytime.

#### Acceptance Criteria

1. WHEN an audio file is uploaded, THE Storage_Service SHALL store it in Amazon S3 with a unique identifier
2. WHEN storing files, THE Storage_Service SHALL use server-side encryption for all uploaded audio files
3. WHEN a user deletes a Lecture, THE System SHALL remove the audio file from S3 and all associated data from the database
4. WHEN accessing stored files, THE System SHALL generate time-limited signed URLs valid for 1 hour
5. WHEN the total storage exceeds 5GB, THE System SHALL notify administrators and prevent new uploads until space is freed

### Requirement 11: Cost Optimization

**User Story:** As a platform operator, I want to minimize operational costs, so that the service remains sustainable during the hackathon period.

#### Acceptance Criteria

1. WHEN processing lectures, THE System SHALL use Groq API for LLM inference to avoid OpenAI API costs
2. WHEN storing audio files, THE Storage_Service SHALL utilize Amazon S3 free tier (5GB) exclusively
3. WHEN the total cost for the hackathon period is calculated, THE System SHALL remain under $5 in total expenses
4. WHEN transcribing audio, THE Audio_Processor SHALL use local Whisper processing to avoid transcription API costs
5. WHEN database operations are performed, THE System SHALL use Supabase free tier limits efficiently

### Requirement 12: Reliability and Error Handling

**User Story:** As a student, I want the system to handle errors gracefully, so that I understand what went wrong and can take corrective action.

#### Acceptance Criteria

1. IF audio transcription fails, THEN THE System SHALL retry up to 3 times before marking the job as failed
2. IF the LLM API is unavailable, THEN THE System SHALL queue the request and retry every 5 minutes for up to 1 hour
3. IF file upload to S3 fails, THEN THE System SHALL display a clear error message and allow the user to retry
4. WHEN any error occurs, THE System SHALL log detailed error information for debugging purposes
5. WHEN the System is operational, THE System SHALL maintain 95% uptime during the demo period

### Requirement 13: Content Accuracy and Quality

**User Story:** As a student, I want accurate study materials, so that I can trust the content for exam preparation.

#### Acceptance Criteria

1. WHEN extracting key concepts, THE Content_Generator SHALL achieve at least 70% accuracy compared to manual extraction
2. WHEN generating MCQs, THE Content_Generator SHALL ensure all questions have exactly one correct answer
3. WHEN formatting mathematical formulas, THE Content_Generator SHALL use proper LaTeX or markdown math syntax
4. WHEN generating flashcards, THE Content_Generator SHALL ensure questions and answers are contextually related to the lecture
5. WHEN creating notes, THE Content_Generator SHALL maintain the logical flow and structure of the original lecture

### Requirement 14: Security and Data Privacy

**User Story:** As a student, I want my data to be secure, so that my lecture content and personal information remain private.

#### Acceptance Criteria

1. THE System SHALL serve all content exclusively over HTTPS connections
2. WHEN storing passwords, THE Authentication_Service SHALL hash them using bcrypt with a cost factor of at least 12
3. WHEN transmitting JWT tokens, THE System SHALL include them in HTTP-only cookies or Authorization headers only
4. WHEN accessing the API, THE System SHALL implement rate limiting of 100 requests per minute per user
5. WHEN a user's session is active, THE System SHALL automatically log out the user after 30 minutes of inactivity

### Requirement 15: Progress Tracking and Analytics

**User Story:** As a student, I want to track my learning progress, so that I can identify areas that need more attention.

#### Acceptance Criteria

1. WHEN a user completes a quiz, THE System SHALL record the score and timestamp in the database
2. WHEN displaying analytics, THE System SHALL show quiz performance trends over time
3. WHEN a user performs poorly on specific topics, THE System SHALL identify and highlight those topics as weak areas
4. WHEN a user reviews flashcards, THE System SHALL track which cards were marked as difficult or easy
5. WHEN displaying progress, THE System SHALL calculate and show the percentage of materials reviewed for each Lecture
