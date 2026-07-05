import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction, QGraphicsDropShadowEffect
from PyQt5.QtGui import QMovie, QPixmap, QCursor, QColor
from PyQt5.QtCore import Qt, QPoint, QTimer

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. 窗口属性初始化
        self.init_window()
        
        # 2. 交互数据初始化
        self.is_free_moving = True  # 是否允许自由活动
        self.current_state = 0      # 0: 待命, 1: 向左走, 2: 向右走
        self.move_speed = 2         # 移动速度（像素/帧）
        
        # 3. 气泡台词库
        self.sayings = [
            "无体育，不清华！🏃‍♂️",
            "今天你锻炼了吗？🏋️‍♂️",
            "努力学习中，请勿打扰~ 📚",
            "贴贴~ ❤️",
            "再点我，我就要生气啦！😡",
            "今天也要加油鸭！🦆"
        ]
        
        # 4. 载入UI元素（气泡 + 宠物）
        self.init_ui()
        
        # 5. 定时器配置
        self.init_timers()
        
        self.drag_position = QPoint()

    def init_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 获取屏幕分辨率，让桌宠初始位置处于屏幕右下角
        screen = QApplication.desktop().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        
        # 窗口大小：宽 220，高 290
        self.pet_width = 220
        self.pet_height = 290
        
        # 初始位置：屏幕右下角
        self.move(self.screen_width - self.pet_width - 100, self.screen_height - self.pet_height - 80)
        self.resize(self.pet_width, self.pet_height)

    def init_ui(self):
        # --- 1. 对话气泡 QLabel ---
        self.talk_label = QLabel(self)
        self.talk_label.setGeometry(10, 5, 200, 75) 
        
        self.talk_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 240);
            color: #512DA8;
            border: 2px solid #9575CD;
            border-radius: 12px;
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            font-size: 14px;
            font-weight: bold;
            padding: 8px;
        """)
        self.talk_label.setAlignment(Qt.AlignCenter)
        self.talk_label.setWordWrap(True)

        # 物理阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)             
        shadow.setColor(QColor(0, 0, 0, 50)) 
        shadow.setOffset(0, 3)               
        self.talk_label.setGraphicsEffect(shadow)

        self.talk_label.hide() 

        # --- 2. 宠物图片 QLabel ---
        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(10, 85, 200, 200) 
        
        # 【打包兼容版路径获取】
        # 判断如果是以打包后的 .exe 运行，则寻找 .exe 同级目录下的图片；如果是运行 .py，则在脚本同级目录下寻找
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)  
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))  
        
        # 将图片路径与文件夹路径拼接
        gif_path = os.path.join(current_dir, "pet.gif")
        png_path = os.path.join(current_dir, "pet.png")
        
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.pet_label.setMovie(self.movie)
            self.movie.start()
        elif os.path.exists(png_path):
            pixmap = QPixmap(png_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pet_label.setPixmap(scaled_pixmap)
        else:
            self.pet_label.setText("未找到图片")
            self.pet_label.setStyleSheet("color: white; background: gray;")
            self.pet_label.setAlignment(Qt.AlignCenter)

    def init_timers(self):
        # 计时器1：控制位置移动
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.update_movement)
        self.move_timer.start(40)
        
        # 计时器2：随机改变活动状态
        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.change_behavior)
        self.behavior_timer.start(3000)
        
        # 计时器3：控制对话气泡显示时长
        self.talk_timer = QTimer()
        self.talk_timer.timeout.connect(self.talk_label.hide)

    # --- 行为逻辑控制 ---
    def change_behavior(self):
        if not self.is_free_moving:
            self.current_state = 0
            return
        self.current_state = random.choices([0, 1, 2], weights=[40, 30, 30])[0]

    def update_movement(self):
        if self.current_state == 0:
            return
        
        current_x = self.x()
        
        if self.current_state == 1: # 向左走
            next_x = current_x - self.move_speed
            if next_x < 0: # 碰到屏幕左边缘，往右反弹
                self.current_state = 2
            else:
                self.move(next_x, self.y())
                
        elif self.current_state == 2: # 向右走
            next_x = current_x + self.move_speed
            if next_x > self.screen_width - self.pet_width: # 碰到屏幕右边缘，往左反弹
                self.current_state = 1
            else:
                self.move(next_x, self.y())

    # --- 点击互动 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            self.show_dialog()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))

    def show_dialog(self):
        words = random.choice(self.sayings)
        self.talk_label.setText(words)
        self.talk_label.show()
        self.talk_timer.start(3000)

    # --- 菜单控制 ---
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        toggle_text = "原地待命" if self.is_free_moving else "自由活动"
        toggle_action = QAction(toggle_text, self)
        toggle_action.triggered.connect(self.toggle_move_state)
        menu.addAction(toggle_action)
        
        exit_action = QAction("退出桌宠", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        
        menu.exec_(event.globalPos())

    def toggle_move_state(self):
        self.is_free_moving = not self.is_free_moving
        if not self.is_free_moving:
            self.current_state = 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 强制防止因隐藏任务栏图标而导致程序判定无主窗口而闪退
    app.setQuitOnLastWindowClosed(False)
    
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())