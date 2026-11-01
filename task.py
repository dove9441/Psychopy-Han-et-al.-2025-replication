import math
import random
import pandas as pd
from psychopy import core, event, monitors, visual, colors


CLOCK_ANGLES_DEG = [-120, 180, 120, 60, 0, -60]  # 7,9,11,1,3,5 o'clock
ANGLE_TO_KEY = {
	-120: "n",
	180: "h",
	120: "u",
	60: "i",
	0: "o",
	-60: "space",
}



def build_sample_squares(win):
	"""
	 Stimuli were 1◦colored squares, with two possible colors (color A, and color B) at each location, randomized
	daily to prevent long-term memorization. Six item locations (roughly 1, 3, 5, 7, 9, and 11 o’clock) were used each session that
	were ±75 angular degrees from the horizontal meridian and 4◦ to 6◦ from the fixation point (Han et al. 2025)
	"""
	# clock_angles_deg = [60, 0, -60, -120, 180, 120]  # 1,3,5,7,9,11 o'clock
	clock_angles_deg = CLOCK_ANGLES_DEG

	# color_list
	color_names = list(colors.colorNames.keys()) # 149 colors
	square_size_deg = 1.0
	squares = []

	# position별 colorset A/B 만들기
	for angle_deg in clock_angles_deg:
		ecc = 4 # 중심으로부터의 거리
		angle_rad = math.radians(angle_deg)
		x = ecc * math.cos(angle_rad)
		y = ecc * math.sin(angle_rad)

		color_a, color_b = random.sample(color_names, 2)

		square_a = visual.Rect(
			win,
			width=square_size_deg,
			height=square_size_deg,
			pos=(x, y),
			fillColor=color_a,
			lineColor=color_a,
			units="deg",
		)
		square_b = visual.Rect(
			win,
			width=square_size_deg,
			height=square_size_deg,
			pos=(x, y),
			fillColor=color_b,
			lineColor=color_b,
			units="deg",
		)
		squares.append((square_a, square_b))
	

	return squares # [(squareA, squareB), (squareA, squareB), ...] for 6 positions


# example trial용 key label
def build_key_labels(win, sample_squares, idx_to_key):
	labels = []
	for i, (square_a, _) in enumerate(sample_squares):
		x, y = square_a.pos
		label_text = idx_to_key[i]
		label = visual.TextStim(
			win,
			text=label_text,
			color="white",
			height=0.35,
			pos=(x + 0.8, y),
			units="deg",
		)
		labels.append(label)
	return labels


def run():
	# MacBook pro 14" -> 30.2cm width
	monitor = monitors.Monitor("labMonitor", width=30.2, distance=100.0) # 거리 임의 설정
	monitor.setSizePix((1280, 1024))

	win = visual.Window(
		size=(1280, 1024),
		fullscr=False,
		monitor=monitor,
		units="deg",
		color="black",
	)

	instruction = visual.TextStim(
		win,
		text="""Your goal is indicating which square changed color by pressing key corresponding to its location.\n
		Please place your right fingers on the keys "n", "h", "u", "i", "o", and left thumb on "space".\n
		Press SPACE to example start""",
		color="white",
		height=0.5,
	)

	fixation_dot = visual.Circle(
		win,
		radius=0.05,
		fillColor="white",
		lineColor="white",
		units="deg",
	)
	fixation_ring = visual.Circle(
		win,
		radius=0.3,
		edges=128,
		lineColor="red",
		lineWidth=3,
		fillColor=None,
		units="deg",
	)

	try:
		correct = []
		RT = []
		answer = []
		user_response = []
		setSize_list = []
		idx_to_key = [ANGLE_TO_KEY[angle] for angle in CLOCK_ANGLES_DEG]

		## Instruction
		instruction.draw()
		win.flip()
		event.waitKeys(keyList=["space"])
		sample_squares = build_sample_squares(win)
		key_labels = build_key_labels(win, sample_squares, idx_to_key)

		## Example trial
		for i in range(3):
			# Fixation
			visual.TextStim(win, text="Fixation", color="white", height=0.8).draw()
			win.flip()
			core.wait(1)
			fixation_dot.draw()
			fixation_ring.draw()
			win.flip()
			core.wait(1)

			# Sample
			visual.TextStim(win, text="Sample", color="white", height=0.8).draw()
			win.flip()
			core.wait(1)
			fixation_dot.draw()
			fixation_ring.draw()

			square_valid = [1, 1, 1, 1, 1, 1]
			selectSet = random.randint(0, 1) # color A or Color B
			square_colorSet = [0, 0, 0, 0, 0, 0]

			# selectSet에 따라 A 또는 B 색으로 그리기
			for i, (squareA, squareB) in enumerate(sample_squares):
				if square_valid[i] == 0:
					continue
				if selectSet == 0:
					squareA.draw()
					square_colorSet[i] = 1
				else:
					squareB.draw()
					square_colorSet[i] = 2
			win.flip()
			core.wait(2)

			# Delay
			visual.TextStim(win, text="Delay", color="white", height=0.8).draw()
			win.flip()
			core.wait(1)
			fixation_dot.draw()
			fixation_ring.draw()
			win.flip()
			core.wait(0.5)
	
			# Test
			visual.TextStim(win, text="Test", color="white", height=0.8).draw()
			win.flip()
			core.wait(1)
			fixation_dot.draw()
			fixation_ring.draw()
			# 랜덤하게 1개 선택 후 색상 변경 (A->B or B->A)
			change_target_idx = random.choice(range(6))
			for i, (squareA, squareB) in enumerate(sample_squares):
				if square_valid[i] == 0: # setSize에 따라 보여주도록 선택되지 않은 사각형
					continue
				if i == change_target_idx:
					if square_colorSet[i] == 1:
						squareB.draw()
					else:
						squareA.draw()
				else:
					if square_colorSet[i] == 1:
						squareA.draw()
					else:
						squareB.draw()
				key_labels[i].draw()

			win.flip()
			response_clock = core.Clock()
			keys = event.waitKeys(
				maxWait=10,
				# -120,180,120,60,0,-60 -> n,h,u,i,o,space
				keyList=["n", "h", "u", "i", "o", "space"],
				timeStamped=response_clock,
			)


			# print response
			if keys is None:
				pass
			else:
				key, rt = keys[0]
				target_key = idx_to_key[change_target_idx]
				is_correct = int(key == target_key)

				visual.TextStim(
					win,
					text=f"Correct: {is_correct},  RT: {rt:.3f}s",
					color="white",
					height=0.5,
				).draw()
				win.flip()
				core.wait(2)
			

	
		## End of example trial
		visual.TextStim(
			win,
			text="Press Space to start the experiment.",
			color="white",
			height=0.8,
		).draw()
		win.flip()
		event.waitKeys(keyList=["space"])
		

		### main experiment

		sample_squares = build_sample_squares(win) # A/B color 초기화
		## Trial loop
		for t in range(30):

			if t % 10 == 0:
				sample_squares = build_sample_squares(win) 


			# 6개 사각형 중 보여질 2~5개 설정
			setSize = random.randint(2,5)
			square_valid = [0, 0, 0, 0, 0, 0] # 0: not shown, 1: shown
			chosen_idxs = random.sample(range(6), k=setSize)
			for idx in chosen_idxs:
				square_valid[idx] = 1

			# Fixation (500ms)
			fixation_dot.draw()
			fixation_ring.draw()
			win.flip()
			core.wait(0.5)

			# Sample (800ms)
			fixation_dot.draw()
			fixation_ring.draw()

			square_colorSet = [0, 0, 0, 0, 0, 0]

			# selectSet에 따라 A 또는 B 색으로 그리기
			for i, (squareA, squareB) in enumerate(sample_squares):
				if square_valid[i] == 0:
					continue
				selectSet = random.randint(0, 1) # color A or Color B
				if selectSet == 0:
					squareA.draw()
					square_colorSet[i] = 1
				else:
					squareB.draw()
					square_colorSet[i] = 2

			win.flip()
			core.wait(2)

			# Delay (800-1000ms)
			fixation_dot.draw()
			fixation_ring.draw()
			win.flip()
			core.wait(random.uniform(0.8, 1.0))
			

			# Test onset(until response)
			fixation_dot.draw()
			fixation_ring.draw()

			# 랜덤하게 1개 선택 후 색상 변경 (A->B or B->A)
			change_target_idx = random.choice(chosen_idxs)
			for i, (squareA, squareB) in enumerate(sample_squares):
				if square_valid[i] == 0:
					continue
				if i == change_target_idx:
					if square_colorSet[i] == 1:
						squareB.draw()
					else:
						squareA.draw()
				else:
					if square_colorSet[i] == 1:
						squareA.draw()
					else:
						squareB.draw()

			win.flip()
			response_clock = core.Clock()
			keys = event.waitKeys(
				maxWait=3,
				# -120,180,120,60,0,-60 -> n,h,u,i,o,space
				keyList=["n", "h", "u", "i", "o", "space",],
				timeStamped=response_clock,
			)

			

			
			# print response
			if keys is None:
				correct.append(0)
				RT.append(None)
				answer.append(None)
				user_response.append(None)
				setSize_list.append(setSize)
			else:
				key, rt = keys[0]
				target_key = idx_to_key[change_target_idx]
				is_correct = int(key == target_key)
				correct.append(is_correct)
				RT.append(f"{rt:.2f}")
				answer.append(target_key)
				user_response.append(key)
				setSize_list.append(setSize)

		# end screen
		end_screen = visual.TextStim(
			win,
			text="Experiment completed.\n\nPress any key to exit.",
			color="white",
			height=0.8,
		)
		end_screen.draw()
		win.flip()
		event.waitKeys()
	except Exception as e:
		print(f"Error: {e}")

	finally:
		pd.DataFrame(
			{
				"correct": correct,
				"RT": RT,
				"setSize": setSize_list,
				"answer": answer,
				"user_response": user_response,
			}
		).to_csv("results.csv", index=True)
		win.close()
		core.quit()


if __name__ == "__main__":
    run()
