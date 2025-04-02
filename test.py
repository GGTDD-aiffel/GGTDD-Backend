from langchain_openai import ChatOpenAI
from app.infrastructure.LLMs.user_generator import UserGenerator
from app.infrastructure.LLMs.recognition_generator import RecognitionGenerator
from app.infrastructure.performance import PerformanceTracker
from app.infrastructure.firebase_repo import FirebaseRepository
from app.domain.user.use_cases import UserUseCase
from app.domain.recognition.use_cases import RecognitionUseCase

tracker = PerformanceTracker()
fbr = FirebaseRepository()
userGenerator = UserGenerator(ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
userUseCase = UserUseCase(fbr, userGenerator)

recognitionGenerator = RecognitionGenerator(ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
recognitionUseCase = RecognitionUseCase(recognitionGenerator, fbr)

user = userUseCase.create_user('wmnNRPATx5y8p5mp2rca')
userUseCase.update_tags(user)
userGenerator.generate_prompts(user)

print(user.bio_str)

prompt_index = input("프롬프트 중 선택할 인덱스를 입력하세요: ")
userUseCase.select_prompt(user, int(prompt_index))

print(user.bio_str)

paraphrase = recognitionUseCase.generate_paraphrase("dummy", "체중감량을 위한 운동", user.bio_str)
print(paraphrase)

# paraphrase = tracker.measure(task_generator._process_paraphrase,
#                             #   timeout=15,
#                               user=user,
#                               input_to_paraphrase="체중감량을 위한 운동")

# for i, para in enumerate(paraphrase):
#     print(f"{i}: {para}")

# paraphrase_index = input("패러프레이즈 중 선택할 인덱스를 입력하세요: ")
# task = tracker.measure(task_generator.process,
#                        timeout=15,
#                        user=user,
#                        task_input=paraphrase[int(paraphrase_index)],
#                        subtask_num=5)

# print(task)
# subtask_num = input("하위 작업의 개수를 입력하세요: ")
# task_generator.process(timeout=15,
#                        processor_func=task_generator._process_subtasks,
#                        user=user,
#                        task_to_breakdown=task,
#                        subtask_num=int(subtask_num))
# print(task)
# task_to_break = input("하위 작업을 추가할 상위 작업의 인덱스를 입력하세요: ")
# tracker.measure(task_generator.process,
#                 timeout=15,
#                 processor_func=task_generator._process_subtasks,
#                 user=user,
#                 task_to_breakdown=task.get_subtask(int(task_to_break)-1),
#                 subtask_num=3)
# print(task)

# tracker.measure(task_commenter.process, 
#                 user=user, 
#                 task_to_comment=task)
# # task_commenter.process(user=user, task_to_comment=task.get_subtask(4))

# print(task)

# print(tracker.get_summary())