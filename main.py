#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf
import os
import sys
import detectHardware
import driverMatcher
import listboxHelper

EXEC_FOLDER = os.path.realpath(os.path.dirname(__file__)) + "/"
builder = Gtk.Builder()
builder.add_from_file(EXEC_FOLDER + "ui.glade")
HOME = os.environ.get('HOME')

# settings = Gtk.Settings.get_default()
# settings.set_property("gtk-application-prefer-dark-theme", True)

class App(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self,
								 application_id="org.gabmus.gcrawler",
								 flags=Gio.ApplicationFlags.FLAGS_NONE)
		self.connect("activate", self.activateCb)

	def do_startup(self):
		# start the application
		Gtk.Application.do_startup(self)

	def activateCb(self, app):
		window = builder.get_object("window")
		window.set_wmclass("Cab-Driver", "Cab-Driver")
		window.set_title("Cab-Driver")
		app.add_window(window)
		appMenu = Gio.Menu()
		appMenu.append("About", "app.about")
		appMenu.append("Quit", "app.quit")
		about_action = Gio.SimpleAction.new("about", None)
		about_action.connect("activate", self.on_about_activate)
		builder.get_object("aboutdialog").connect(
			"delete-event", lambda *_: builder.get_object("aboutdialog").hide() or True)
		app.add_action(about_action)
		quit_action = Gio.SimpleAction.new("quit", None)
		quit_action.connect("activate", self.on_quit_activate)
		app.add_action(quit_action)
		app.set_app_menu(appMenu)
		window.show_all()

	def on_about_activate(self, *agrs):
		builder.get_object("aboutdialog").show()

	def on_quit_activate(self, *args):
		self.quit()

app = App()

#dictionary for storing current config
current_config={
	'manualauto': None, # valid: 'manual', 'auto'
	'hybrid': False,
	'distro': None,
	'gpu1_vendor': None,
	'gpu2_vendor': None,
	'gpu1_model': None,
	'gpu2_model': None,
	'packages': None,
}

mainstack_special_pages = [ # page indexes where the next button should be locked
	1, # choose auto detect or manual config
]

mainstack_interact_pages = [ # pages that need user interaction
	2, # manual config menu, need to finish configuration
	3, # autodetect page, need to press autodetect button
]

special_pages_directions = {
	-3: -2, # coming back from auto config, to choose manual or auto config
	2: +2 # next from manual config, to packages needed page
}

IMG_PATH = EXEC_FOLDER+'/img/'
VENDOR_ICONS = {
	'NVIDIA Corporation': IMG_PATH+'nvidia-small.jpg',
	'Intel Corporation': IMG_PATH+'intel-small.jpg',
	'Advanced Micro Devices, Inc. [AMD/ATI]': IMG_PATH+'amd-small.jpg'
}

main_stack = builder.get_object('mainStack')
main_stack_children = main_stack.get_children()

next_button = builder.get_object('nextButton')
back_button = builder.get_object('backButton')

detected_hw_label = builder.get_object('detectedHwLabel')
hardware_listbox = builder.get_object('hardwareListbox')

needed_packages_label = builder.get_object('neededPackagesLabel')

# fill static listboxes
# manual or auto configuration
manual_auto_config_listbox = builder.get_object('manualOrAutoChooseListbox')
moac_labels = [
	'Detect hardware automatically',
	'Select hardware manually'
]
moac_pics = [
	IMG_PATH+'search.svg',
	IMG_PATH+'touch.svg'
]
moac_values = [
	'auto',
	'manual'
]
for i in range(0,2):
	row=listboxHelper.make_image_row(moac_labels[i], moac_pics[i])
	row.value = moac_values[i]
	manual_auto_config_listbox.add(row)
manual_auto_config_listbox.show_all()

# fill manual distro popover listbox
manual_distro_button = builder.get_object('manualChooseDistroButton')
manual_distro_listbox = builder.get_object('manualChooseDistroPopoverListbox')
manual_distro_label = builder.get_object('manualDistroLabel')
manual_distro_icon = builder.get_object('manualDistroIcon')
for d in driverMatcher.DISTROS:
	row = listboxHelper.make_image_row(d.capitalize(), IMG_PATH+'/'+d+'.png')
	row.value = d
	manual_distro_listbox.add(row)
	row.show_all()
manual_distro_listbox.show_all()
manual_distro_listbox.select_row(None)
manual_distro_popover = builder.get_object('manualChooseDistroPopover')

# fill vendor listbox
def fill_vendor_listbox(listbox, gpu1_vendor=None):
	listboxHelper.empty_listbox(listbox)
	for vendor in driverMatcher.VENDORS:
		if not gpu1_vendor == vendor:
			row = listboxHelper.make_image_row(vendor, VENDOR_ICONS[vendor])
			row.value = vendor
			listbox.add(row)
			row.show_all()

manual_gpu1_vendor_listbox = builder.get_object('manualChooseGPU1VendorPopoverListbox')
manual_gpu2_vendor_listbox = builder.get_object('manualChooseGPU2VendorPopoverListbox')
fill_vendor_listbox(manual_gpu1_vendor_listbox)
# gpu2 vendor populated accordingly to gpu1
manual_gpu1_model_listbox = builder.get_object('manualChooseGPU1ModelPopoverListbox')
manual_gpu2_model_listbox = builder.get_object('manualChooseGPU2ModelPopoverListbox')

manual_gpu1_vendor_popover = builder.get_object('manualChooseGPU1VendorPopover')
manual_gpu2_vendor_popover = builder.get_object('manualChooseGPU2VendorPopover')
manual_gpu1_model_popover = builder.get_object('manualChooseGPU1ModelPopover')
manual_gpu2_model_popover = builder.get_object('manualChooseGPU2ModelPopover')

def fill_manual_model_listbox(vendor, listbox):
	listboxHelper.empty_listbox(listbox)
	if vendor == 'NVIDIA Corporation':
		for model in driverMatcher.NVIDIA_FAMILY_CARDS:
			row = listboxHelper.make_row(model)
			row.value=model
			listbox.add(row)
			row.show_all()
	elif vendor == 'Intel Corporation':
		row = listboxHelper.make_row('Any Intel GPU')
		row.value='Any Intel GPU'
		listbox.add(row)
		row.show_all()
	# TODO: add case for AMD GPUs
	else:
		raise ValueError('Vendor not recognised')

def empty_config():
	current_config['manualauto'] = None
	current_config['distro'] = None
	current_config['gpu1_vendor'] = None
	current_config['gpu2_vendor'] = None
	current_config['gpu1_model'] = None
	current_config['gpu2_model'] = None
	current_config['hybrid'] = False
	listboxHelper.empty_listbox(
		builder.get_object('manualResultDistroListbox')
	)
	listboxHelper.empty_listbox(
		builder.get_object('manualResultGPU1Listbox')
	)
	listboxHelper.empty_listbox(
		builder.get_object('manualResultGPU2Listbox')
	)
	listboxHelper.empty_listbox(hardware_listbox)
	builder.get_object('autoDetectWrongMaybeLabel').hide()
	manual_auto_config_listbox.select_row(None)


def is_config_set():
	if (not current_config['hybrid'] or current_config['gpu2_model']) and current_config['gpu1_model'] and current_config['distro']:
		return True
	else:
		return False

packages_to_install_listbox = builder.get_object('packagesToInstallListbox')

class Handler:

	def onDeleteWindow(self, *args):
		app.quit()

	def _set_next_back_btn_state(self):
		# get current child index
		current_child_index = main_stack_children.index(
			main_stack.get_visible_child()
		)

		back_button.set_sensitive(
			current_child_index > 0
		)

		next_button.set_sensitive(
			not current_child_index in mainstack_special_pages and current_child_index < len(main_stack_children)-1
		)

		if current_child_index in mainstack_interact_pages:
			next_button.set_sensitive(is_config_set())

	def _move_stack(self, direction):
		current_child_index = main_stack_children.index(
			main_stack.get_visible_child()
		)
		main_stack.set_visible_child(
			main_stack_children[current_child_index+direction]
		)

		self._set_next_back_btn_state()

	def on_nextButton_clicked(self, button):
		current_child_index = main_stack_children.index(
			main_stack.get_visible_child()
		)
		if current_child_index in mainstack_interact_pages:
			current_config['packages'] = driverMatcher.get_packages(current_config)
			listboxHelper.empty_listbox(packages_to_install_listbox)
			for p in current_config['packages']:
				row = listboxHelper.make_row(p)
				packages_to_install_listbox.add(row)
				row.show_all()
		if current_child_index in special_pages_directions.keys():
			self._move_stack(special_pages_directions[current_child_index])
		else:
			self._move_stack(1)

	def on_backButton_clicked(self, button):
		current_child_index = -1 * (main_stack_children.index(
			main_stack.get_visible_child()
		))
		if current_child_index*-1 in mainstack_interact_pages:
			empty_config()
		if current_child_index == -4 and current_config['manualauto'] == 'manual':
			self._move_stack(-2)
		elif current_child_index in special_pages_directions.keys():
			self._move_stack(special_pages_directions[current_child_index])
		else:
			self._move_stack(-1)

	def on_detectHwButton_clicked(self, button):
		hw_l = detectHardware.get_relevant_info()
		# empty hardware list before filling
		listboxHelper.empty_listbox(hardware_listbox)

		# add distro row
		distro_row=listboxHelper.make_image_row(
			driverMatcher.get_distro().capitalize(),
			IMG_PATH+'/'+driverMatcher.get_distro()+'.png')
		hardware_listbox.add(distro_row)
		distro_row.show_all()
		hardware_listbox.show()
		for i in hw_l:
			row=listboxHelper.make_image_row(i[0]+' '+i[1], VENDOR_ICONS[i[0]])
			hardware_listbox.add(row)
			row.show_all()
		builder.get_object('autoDetectWrongMaybeLabel').show()

		current_config['hybrid'] = (len(hw_l) > 1)
		current_config['distro'] = driverMatcher.get_distro()
		current_config['gpu1_vendor'] = hw_l[0][0]
		current_config['gpu1_model'] = hw_l[0][1]
		if current_config['hybrid']:
			current_config['gpu2_vendor'] = hw_l[1][0]
			current_config['gpu2_model'] = hw_l[1][1]
		self._set_next_back_btn_state()

	def on_manualOrAutoChooseListbox_row_selected(self, list, row):
		if row.value:
			current_config['manualauto']=row.value
		if row.value == 'manual':
			self._move_stack(1)
		else:
			self._move_stack(2)
		# next_button.set_sensitive(True)

	def on_manualChooseDistroPopoverListbox_row_selected(self, list, row):
		manual_distro_popover.hide()
		distro_result_listbox=builder.get_object('manualResultDistroListbox')
		listboxHelper.empty_listbox(distro_result_listbox)
		nrow = listboxHelper.make_image_row(
			row.value.capitalize(),
			IMG_PATH+'/'+row.value+'.png'
		)
		distro_result_listbox.add(nrow)
		nrow.show_all()
		current_config['distro'] = row.value
		if current_config['gpu1_model'] and (not current_config['hybrid'] or current_config['gpu2_model']):
			next_button.set_sensitive(True)
		else:
			next_button.set_sensitive(False)

	def on_manualChooseDistroButton_clicked(self, button):
		if not manual_distro_popover.get_visible():
			manual_distro_popover.show()

	def on_manualChooseGPU1VendorButton_clicked(self, button):
		if not manual_gpu1_vendor_popover.get_visible():
			manual_gpu1_vendor_popover.show()

	def on_manualChooseGPU1ModelButton_clicked(self, button):
		if not manual_gpu1_model_popover.get_visible():
			manual_gpu1_model_popover.show()

	def on_manualChooseGPU2VendorButton_clicked(self, button):
		if not manual_gpu2_vendor_popover.get_visible():
			manual_gpu2_vendor_popover.show()

	def on_manualChooseGPU2ModelButton_clicked(self, button):
		if not manual_gpu2_model_popover.get_visible():
			manual_gpu2_model_popover.show()

	def on_manualChooseGPU1VendorPopoverListbox_row_activated(self, list, row):
		listboxHelper.empty_listbox(
			builder.get_object('manualResultGPU1Listbox')
		)
		listboxHelper.empty_listbox(
			builder.get_object('manualResultGPU2Listbox')
		)
		current_config['gpu1_model'] = None
		current_config['gpu2_model'] = None
		next_button.set_sensitive(False)
		fill_manual_model_listbox(row.value, manual_gpu1_model_listbox)
		current_config['gpu1_vendor'] = row.value
		if current_config['hybrid']:
			builder.get_object('GPU2Box').show()
		fill_vendor_listbox(
			manual_gpu2_vendor_listbox,
			row.value
		)
		manual_gpu1_vendor_popover.hide()
		builder.get_object('manualChooseGPU1ModelButton').set_sensitive(True)

	def on_manualChooseGPU1ModelPopoverListbox_row_activated(self, list, row):
		gpu1_result_listbox = builder.get_object('manualResultGPU1Listbox')
		listboxHelper.empty_listbox(gpu1_result_listbox)
		nrow = listboxHelper.make_image_row(
			current_config['gpu1_vendor']+' '+row.value,
			VENDOR_ICONS[current_config['gpu1_vendor']]
		)
		gpu1_result_listbox.add(nrow)
		nrow.show_all()
		current_config['gpu1_model'] = row.value
		manual_gpu1_model_popover.hide()
		if (not current_config['hybrid'] or current_config['gpu2_model']) and current_config['distro']:
			next_button.set_sensitive(True)
		else:
			next_button.set_sensitive(False)

	def on_manualChooseGPU2VendorPopoverListbox_row_activated(self, list, row):
		listboxHelper.empty_listbox(
			builder.get_object('manualResultGPU2Listbox')
		)
		next_button.set_sensitive(False)
		current_config['gpu2_model'] = None
		fill_manual_model_listbox(row.value, manual_gpu2_model_listbox)
		current_config['gpu2_vendor'] = row.value
		manual_gpu2_vendor_popover.hide()
		builder.get_object('manualChooseGPU2ModelButton').set_sensitive(True)

	def on_manualChooseGPU2ModelPopoverListbox_row_activated(self, list, row):
		gpu2_result_listbox = builder.get_object('manualResultGPU2Listbox')
		listboxHelper.empty_listbox(gpu2_result_listbox)
		nrow = listboxHelper.make_image_row(
			current_config['gpu2_vendor']+' '+row.value,
			VENDOR_ICONS[current_config['gpu2_vendor']]
		)
		gpu2_result_listbox.add(nrow)
		nrow.show_all()
		current_config['gpu2_model'] = row.value
		manual_gpu2_model_popover.hide()
		if current_config['distro'] and current_config['gpu1_model']:
			next_button.set_sensitive(True)

	def on_manualHybridGFXSwitch_state_set(self, switch, state):
		if state:
			current_config['hybrid']=True
			if current_config['gpu1_model'] and current_config['gpu1_vendor']:
				builder.get_object('GPU2Box').show()
			else:
				builder.get_object('GPU2Box').hide()
			if current_config['gpu2_model'] and current_config['gpu1_model'] and current_config['distro']:
				next_button.set_sensitive(True)
			else:
				next_button.set_sensitive(False)
		else:
			current_config['hybrid']=False
			builder.get_object('GPU2Box').hide()
			listboxHelper.empty_listbox(
				builder.get_object('manualResultGPU2Listbox')
			)
			if current_config['gpu1_model'] and current_config['distro']:
				next_button.set_sensitive(True)
			else:
				next_button.set_sensitive(False)

builder.connect_signals(Handler())


if __name__ == "__main__":
	app.run(sys.argv)
