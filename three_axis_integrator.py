class three_axis_integrator:

	def __init__(self):
		self.reset_all_axes()
		self.reset_circle_trace()
		self.reset_medial_rotation()

	def reset_all_axes(self):
		self.reset_x()
		self.reset_y()
		self.reset_z()

	def reset_x(self):
		self.theta_x = 0
		self.integrating_x = False

	def reset_y(self):
		self.theta_y = 0
		self.integrating_y = False

	def reset_z(self):
		self.theta_z = 0
		self.integrating_z = False

	def reset_circle_trace(self):
		self.theta_circle_trace = 0
		self.integrating_circle_trace = False

	def reset_medial_rotation(self):
		self.medial_rotation_check = False

		#renamed diff_check
		self.post_zero_crossing_sample_counter = 0
		self.theta_z_at_crossing = 0

		self.medial_rotation_timeout_counter = 0

	# add member variables for Medial Rotation gesture?? yaw?
