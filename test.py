from langchain_openai import ChatOpenAI
# from app.infrastructure.LLMs import SceneGenerator, TaskGenerator, TaskCommenter
from app.infrastructure.LLMs.UserGenerator import UserGenerator
from app.infrastructure.performance import PerformanceTracker
from app.infrastructure.firebase_repo import FirebaseRepository
from app.domain.user.use_cases import UserUseCase

# scene_generator = SceneGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
# task_generator = TaskGenerator(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
# task_commenter = TaskCommenter(llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
tracker = PerformanceTracker()
fbr = FirebaseRepository()
userGenerator = UserGenerator(ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
userUseCase = UserUseCase(fbr, userGenerator)

user = userUseCase.create_user('wmnNRPATx5y8p5mp2rca')
user.generate_prompts(userGenerator)

print(user)
print(user.metadata_str)

# scenes = scene_generator.process(user=user,
#                                  timeout=15,
#                                  scenes=["출퇴근길",
#                                          "근무",
#                                          "휴식",
#                                          "공부",
#                                          "게임",
#                                          "유튜브 시청",
#                                          "애완동물 돌보기"])
# user.append_scenes(scenes)
# user.collect_tags()

# responses = tracker.measure(user.generate_prompt, timeout=60)

# for i, response in enumerate(responses):
#     print(f"{i}: {response}")

# prompt_index = input("프롬프트 중 선택할 인덱스를 입력하세요: ")
# user.set_prompt(responses=responses, index=int(prompt_index))
# print(user)

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