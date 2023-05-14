import random
import pygame
import math
from datetime import datetime
from datetime import timedelta


##########################################################################
# 기본 초기화
pygame.init()

# 시작시간(틱)
start_ticks = pygame.time.get_ticks()

BLACK = (0,0,0) # 벽
WHITE = (255,255,255) # 배경

#블록 색깔들
RED = (255,0,0)
ORANGE = (255,128,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
SKYBLUE = (0,255,255)
PINK = (255,0,255)
GRAY = (153,153,153)

init_key_list = ["A","B","C","D","E","F","G"]

Block_Colors = {"A" : RED, 
                "B" : ORANGE,
                "C" : YELLOW, 
                "D" : GREEN,
                "E" : BLUE, 
                "F" : SKYBLUE,
                "G" : PINK} # 각 블록의 색깔정보 담고있는 딕셔너리

# 스크린 블록 한변 길이
screen_Block_size = 30


# 화면에 남겨진 블록들 정보에 대한 변수
list_leaved_blocks_coordi = [] # 충돌처리를 위해 화면에 남은 블록들의 좌표정보만 담는 리스트
list_leaved_blocks_data = [] # 화면에 남겨질 각 블록 [위치~,색상] 쌍으로 담는 딕셔너리

# 겹침확인
block_Overlaped = 0

# 화면 설정
screen_size = (570,660) # 화면 사이즈 19 * 22 블록 / 블록 사이즈 30 * 30
screen = pygame.display.set_mode(screen_size)

# 화면 타이틀 설정
pygame.display.set_caption("HYO_Tetris")


# 블록 그리기 함수
def draw_block(screen, color, position):
    for pos in position:
        block = pygame.Rect((pos[0] * screen_Block_size , pos[1] * screen_Block_size),\
            (screen_Block_size, screen_Block_size))
        pygame.draw.rect(screen, color, block)


def app_to_leaved_list(list:list): # 충돌처리용 leaved_blocks_coordi에 append하는 함수
    list_len = len(list)
    for i in range(0,list_len):
        list_leaved_blocks_coordi.append(list[i])

def remove_from_leaved_list(list:list):
    for comp in list:
        if comp in list_leaved_blocks_coordi:
            list_leaved_blocks_coordi.remove(comp)
    
        

def app_to_leaved_data(list:list, color): # 블록그리기용 leaved_blocks_data에 좌표와 컬러 append
    color_app = [color]
    list_leaved_blocks_data.append(list + color_app)

def remove_from_leaved_data(list:list):
    for comp in list: 
        for i in list_leaved_blocks_data:
            if comp in i:
                i.remove(comp)
    

def coordi_down(row:list): #블록을 지운뒤 아래가 비어있다면 윗줄 블록들을 아래로 하강시키는 함수(좌표)
    list_Ndown_blocks = []
    list_to_remove = []
    list_len = len(list_leaved_blocks_coordi)

    for i in range(0,list_len):
        if list_leaved_blocks_coordi[i][1] < row[0][1]: # 지워지는 열보다 위에 있는(y좌표 작은)좌표들
            if list_leaved_blocks_coordi[i][0] != 0 \
                and list_leaved_blocks_coordi[i][0] != 11 and list_leaved_blocks_coordi[i][1] != 21:

                list_to_remove.append(list_leaved_blocks_coordi[i])
                list_Ndown_blocks.append((list_leaved_blocks_coordi[i][0] , list_leaved_blocks_coordi[i][1] + 1))

    for comp in list_to_remove:
        list_leaved_blocks_coordi.remove(comp)

    for comp in list_Ndown_blocks:
        list_leaved_blocks_coordi.append(comp)
    

def data_down(row:list):
    list_Ndown_blocks = []
    list_to_remove = []
    list_len = len(list_leaved_blocks_data)
    
    for i in range(0,list_len):
        list_to_remove_comp = []
        list_Ndown_blocks_comp = []

        for j in range(0,len(list_leaved_blocks_data[i])-1):
            if list_leaved_blocks_data[i][j][1] < row[0][1]: # 지워지는 열보다 위에 있는(y좌표 작은)좌표들
                list_to_remove_comp.append(list_leaved_blocks_data[i][j])
                list_Ndown_blocks_comp.append((list_leaved_blocks_data[i][j][0] ,\
                     list_leaved_blocks_data[i][j][1] + 1))

        if len(list_to_remove_comp) != 0:
            list_to_remove_comp.append(list_leaved_blocks_data[i][-1])
            list_to_remove.append(list_to_remove_comp)
            
        if len(list_Ndown_blocks_comp) != 0:
            list_Ndown_blocks_comp.append(list_leaved_blocks_data[i][-1])
            list_Ndown_blocks.append(list_Ndown_blocks_comp)

    for i in range(0,len(list_to_remove)):
        for j in range(0,len(list_to_remove[i])-1):
            for k in range(0,len(list_leaved_blocks_data)):
                if list_to_remove[i][j] in list_leaved_blocks_data[k]:
                    list_leaved_blocks_data[k].remove(list_to_remove[i][j])
    

    for comp in list_Ndown_blocks:
        list_leaved_blocks_data.append(comp)

    for i in list_leaved_blocks_data:
        if len(i) == 1:
            list_leaved_blocks_data.remove(i)
    
        
# 화면(Field 클래스)
class Field:

    def __init__(self,width,height): # 메인 필드의 경우 19,22
        self.Field_game_score = 0
        self.Field_size = screen_size
        self.Field_main_x_axis = [num for num in range(0,width)] # 메인 플레이화면 x축 좌표 리스트
        self.Field_main_y_axis = [num for num in range(0,height)] # 메인 플레이화면 y축 좌표 리스트
        self.Field_main_plot = []
        self.Field_main_rows = [] # 플레이화면 열(row) 좌표들
        self.frame_color = BLACK

        for i in self.Field_main_x_axis:
            for j in self.Field_main_y_axis:
                self.Field_main_plot.append((i,j))
        
        for row_num in range(0,21):
            row = []
            for i in self.Field_main_plot:
                if i[1] == row_num and i[0] > 0 and i[0] < 11:
                    row.append(i)
            self.Field_main_rows.append(row)
        
        # print(self.Field_main_rows)
    
    def draw_lattice(self):

        for i in self.Field_main_rows:
            for pos in i:
                block = pygame.Rect((pos[0] * screen_Block_size , pos[1] * screen_Block_size),\
                    (screen_Block_size, screen_Block_size))
                pygame.draw.rect(screen, GRAY, block, 1)

    def mainField_coordi(self): # 화면에 표시할 메인프레임(테두리) 좌표들을 리스트 변수로 반환
        list_mainframe_coordi = [] # 프레임 그리기위한 벽좌표
        for plot in self.Field_main_plot: # 화면 좌표 담긴 main_plot / plot :(x,y)
            if plot[0] == 0 or  plot[0] == 11:
                list_mainframe_coordi.append(plot)
            elif plot[1] == 21 and plot[0] <= 11:
                list_mainframe_coordi.append(plot)
        if len(list_leaved_blocks_coordi) < len(list_mainframe_coordi):
            app_to_leaved_list(list_mainframe_coordi)
        return list_mainframe_coordi

    def sideBoard_coordi(self):
        list_sideBoard_coordi = [] # 사이드보드(스코어, 다음블록)테두리 좌표
        for plot in self.Field_main_plot:
            if plot[0] >= 12:
                if plot[0] == 18:
                    list_sideBoard_coordi.append(plot)
                elif plot[1] == 0 or plot[1] == 5 or plot[1] == 21:
                    list_sideBoard_coordi.append(plot)
        return list_sideBoard_coordi
             
    def blockBoard_coordi(self):
        list_blockBoard_coordi = [] # 사이드보드(스코어, 다음블록)테두리 좌표
        for plot in self.Field_main_plot:
            if plot[0] >= 12 and plot[0] <= 17:
                if plot[1] >= 8 and plot[1]<=13: # (12,10)~(17,10) 
                    if plot[1] == 8 or plot[1] == 13:
                        list_blockBoard_coordi.append(plot)
                    elif plot[0] == 12 or plot[0] == 17:
                        list_blockBoard_coordi.append(plot)


        return list_blockBoard_coordi
    

    
    def mainField_blockremove(self):
        rows_to_remove = []
        for row in self.Field_main_rows:
            num = 0
            for comp in row:
                if comp in list_leaved_blocks_coordi:
                    num += 1
            if num == 10: # 한줄 다 차있으면
                rows_to_remove.append(row)
                self.Field_game_score += 1000     
                remove_from_leaved_data(row)
                remove_from_leaved_list(row)
                coordi_down(row)
                data_down(row)

    

class Block:

    def __init__(self, Block_key): #블록 딕셔너리에서 키값(알파벳) 받아서 블록 데이터 받아옴
        
        self.block_key = Block_key
        self.key_list = ["A","B","C","D","E","F","G"]
        self.pos_x = 5                     
        self.pos_x_before_rotate = 0
        self.pos_y = 0

        self.to_left = 0
        self.to_right = 0
        self.to_x = 0
        self.to_down = 0

        self.index = 0 # 블록 회전시 변경되는 모양들의 번호, 0번이 기본
        self.index_next = 0
        self.list_block_coordi = []
        self.list_coordi_before_rotate = [] # 스페이스바 누르기 전, 회전 전 좌표 / 회전불가할시 다시 이좌표로
        self.color = Block_Colors.get("{}".format(self.block_key))
        self.block_Data = dic_Blocks.get("{}".format(self.block_key)) # 딕셔너리에 있는 해당 키의 블록데이터 / 블록 종류
        self.list_offset_x = [] # 좌우 벽충돌 처리를 위한 블록 x offset 리스트
        self.offset_size = [num for num in range(0,int(math.sqrt(len(self.block_Data[0]))))] # 블록데이터를 x*x 행렬로 생각했을 때 한 변 범위

    def key_change(self): # 블록 키값 바꾸는 함수
        self.block_key = self.key_list[rand_next_block_key]
        self.color = Block_Colors.get("{}".format(self.block_key))
        self.block_Data = dic_Blocks.get("{}".format(self.block_key))
        self.offset_size = [num for num in range(0,int(math.sqrt(len(self.block_Data[0]))))]
        pass

    def coordi_set(self): # 화면에 표시할 블록 좌표갱신
        self.list_block_coordi = []
        self.list_offset_x = [] # 블록 인덱스가 바뀔때마다 갱신될 x좌표 담을 리스트
        self.list_offset_y = []

        for i in range(0,len(self.block_Data[self.index])): #index 번 블록 길이만큼, 즉 현재 블록 행렬 내부요소 조사하기 위한 범위
            if self.block_Data[self.index][i] == 1: # 만약 index 번 블록의 i번째 요소가 1일경우
                self.offset_x = int(i%len(self.offset_size)) #i번을 offset 길이로 나눈 나머지가 x좌표
                self.offset_y = int(i/len(self.offset_size)) #i번을 offset 길이로 나눈 값이 y좌표
                self.list_offset_x.append(self.offset_x)
                self.list_offset_y.append(self.offset_y)
                self.list_offset_x.sort()
                self.list_offset_y.sort()
                self.list_block_coordi.append((self.pos_x + self.offset_x, self.pos_y + self.offset_y))


    def check_Overlaped(self): # 현재 블럭의 좌표정보 받아와서 좌,우 아래 한칸과 비교함
        list_blocks_len = [num for num in range(0,len(self.list_block_coordi))]# 블럭 리스트 길이만큼 0부터 n 포함하는 리스트
        list_Ndown_blocks = []
        list_Nleft_blocks = []
        list_Nright_blocks = []
        Nleft = 0 # 왼쪽으로 갈수 있는상태 나타내는 변수
        Nright = 0 # 오른쪽으로 갈수 있는상태
        Ndown = 0 # 아래로 갈수 있는 상태
        
        for i in list_blocks_len: 
            list_Ndown_blocks.append((self.list_block_coordi[i][0] , self.list_block_coordi[i][1] + 1))

        for i in list_blocks_len: 
            list_Nleft_blocks.append((self.list_block_coordi[i][0] - 1 , self.list_block_coordi[i][1]))
        
        for i in list_blocks_len: 
            list_Nright_blocks.append((self.list_block_coordi[i][0] + 1 , self.list_block_coordi[i][1]))

        
        for comp in list_Nleft_blocks:
            if comp in list_leaved_blocks_coordi:
                Nleft = 1
                break
            
        for comp in list_Nright_blocks:
            if comp in list_leaved_blocks_coordi:
                Nright = 1
                break

            # 아래쪽 이동
        for comp in list_Ndown_blocks:
            if comp in list_leaved_blocks_coordi:
                Ndown = 1
                break

        return Nleft, Nright, Ndown

    def Overlap(self):
        self.coordi_set()
        overlap = False
        for comp in block.list_block_coordi:
            if comp in list_leaved_blocks_coordi:
                overlap = True
                break

        return overlap
    
    def Rotate(self):
        self.list_coordi_before_rotate = self.list_block_coordi # 회전시키기 전 좌표를 저장
        self.pos_x_before_rotate = self.pos_x # x좌표도 기억(초기화할때 들어가므로)

        if self.index < len(self.block_Data) - 1:
            self.index += 1
        else: self.index = 0 # 좌우가 같이 겹치는 경우가 아니라면 블록 인덱스값 증가

        overlap = self.Overlap() # 블럭 회전후 생긴 좌표에서 겹치는가? / 좌표 갱신 self.coordi_set() 포함
        i = 1
        num = len(self.offset_size)
        shift = -1 # -1이면 왼쪽좌표로 이동, 1이면 오른쪽 좌표로 이동

        while overlap and num > 0:
            if shift == -1:
                self.pos_x -= i
                shift *= -1
                i += 1
                num -= 1
                overlap = self.Overlap()
                
            else:
                self.pos_x += i
                shift *= -1
                i += 1
                num -= 1
                overlap = self.Overlap()
    
                
        if overlap == True: # 좌표 좌우로 이동시켜도 겹치면
            if self.index == 0:
                self.index = len(self.block_Data) - 1
            else:
                self.index -= 1
            self.list_block_coordi = self.list_coordi_before_rotate
            self.pos_x = self.pos_x_before_rotate
            

        else: # 좌우로 반복적으로 옮겨서 안겹치는 좌표 찾았을때
            if self.pos_x >= 11 or self.pos_x + self.list_offset_x[-1] <= 1: # 화면밖으로 나갈경우 회전 x, 이전좌표 불러옴 
                if self.index == 0:
                    self.index = len(self.block_Data) - 1
                else:
                    self.index -= 1

                self.list_block_coordi = self.list_coordi_before_rotate
        self.coordi_set()

dic_Blocks = {
    "A" : ((0,0,0,0,
            0,0,0,0,
            1,1,1,1,
            0,0,0,0),
            
           (0,0,1,0,
            0,0,1,0,
            0,0,1,0,
            0,0,1,0)), # 일자

    "B" : ((1,0,0,
            1,1,1,
            0,0,0),
            
           (0,1,1,
            0,1,0,
            0,1,0),

           (0,0,0,
            1,1,1,
            0,0,1),

           (0,1,0,
            0,1,0,
            1,1,0),), # ㄴ자

    "C" : ((0,0,1,
            1,1,1,
            0,0,0),
            
           (0,1,0,
            0,1,0,
            0,1,1),

           (0,0,0,
            1,1,1,
            1,0,0),

           (1,1,0,
            0,1,0,
            0,1,0),), # 역ㄴ자

    "D" : ((1,1,0,
            0,1,1,
            0,0,0),
            
           (0,0,1,
            0,1,1,
            0,1,0),), # ㄱㄴ자

    "E" : ((0,1,1,
            1,1,0,
            0,0,0),
            
           (0,1,0,
            0,1,1,
            0,0,1),), # 역ㄱㄴ자

    "F" : ((0,1,0,
            1,1,1,
            0,0,0),
            
           (0,1,0,
            0,1,1,
            0,1,0),

           (0,0,0,
            1,1,1,
            0,1,0),

           (0,1,0,
            1,1,0,
            0,1,0),), # 뻐큐

    "G" : ((1,1,
            1,1),

           (1,1,
            1,1))  # ㅁ자
} # 각 블록의 처음 위치정보 담겨있는 딕셔너리

#FPS
clock = pygame.time.Clock()

last_moved_time = datetime.now() # 현재 시간 구하는 변수(블록 자동하강시 시간간격 체크위해)
level_up_time = datetime.now()

####################################객체선언, 초기화#################################################

rand_init_block_key = random.randint(0,6) # 게임 실행시 첫 블록키
rand_next_block_key = random.randint(0,6) # NEXT에 표시될 블록키(다음 블록)

block = Block(init_key_list[rand_init_block_key]) # 블록객체
Next_block = Block(init_key_list[rand_next_block_key])
main_frame = Field(19,22) # 화면(프레임) 객체



# 폰트 설정
game_font = pygame.font.Font(None, 60)
text_nextBlock = game_font.render("NEXT", True, BLACK)
text_GameOver = game_font.render("Game Over", True, BLACK)

# 블록낙하속도(레벨)
block_down_tick = 1.2

block_x_size = 1
block_y_size = 1

Next_block.coordi_set()

for i in range(0,len(Next_block.list_offset_x)-1):
    if Next_block.list_offset_x[i] != Next_block.list_offset_x[i+1]:
        block_x_size += 1
    
for i in range(0,len(Next_block.list_offset_y)-1):
    if Next_block.list_offset_y[i] != Next_block.list_offset_y[i+1]:
        block_y_size += 1

if len(Next_block.offset_size) != 4:
    Next_block.pos_x = 13 + (4 - block_x_size)/2
    Next_block.pos_y = 9 + (4 -block_y_size)/2 
else:
    Next_block.pos_x = 13
    Next_block.pos_y = 9

Next_block.coordi_set()


###################################################################################################

running = True # 게임 진행중인지 확인하는 변수(진행중이면 True, 아니면 False)
while running:
    
    # print(block_down_tick) # 블록다운속도 출력
    if timedelta(seconds = 15) <= datetime.now() - level_up_time:
        if block_down_tick > 0.3: 
            block_down_tick -= 0.1
            level_up_time = datetime.now()
        else:
            if block_down_tick > 0.05:
                block_down_tick -= 0.005
                level_up_time = datetime.now()
    

    text_game_score = game_font.render(str(main_frame.Field_game_score), True, BLACK)
    dt = clock.tick(30) #프레임 설정
    screen.fill(WHITE)

    # 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False # 창나가기 누르면 종료

        # 키보드 입력(좌우 움직임, 스페이스바)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                block.Rotate()
            if event.key == pygame.K_LEFT:
                block.to_left -= 1 # 2
            if event.key == pygame.K_RIGHT:
                block.to_right += 1 # 2   
            if event.key == pygame.K_DOWN:
                block.to_down += 1 # 2    

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                    block.to_left = 0
            elif event.key == pygame.K_RIGHT:
                    block.to_right = 0
            elif event.key == pygame.K_DOWN:
                    block.to_down = 0

    
    block_Overlaped = block.check_Overlaped() # 4 (a,b,c) 겹침체크 반환
    sum_over = block_Overlaped[0] + block_Overlaped[1] + block_Overlaped[2]
    block.to_x = 0

    if timedelta(seconds = block_down_tick) <= datetime.now() - last_moved_time or block.to_down == 1: # 블록 하강조건
        if block_Overlaped[2] == 0: # 아래쪽 안겹치는경우
            block.pos_y += 1
            last_moved_time = datetime.now() # 4 - (1) 블록 하강

        else: # 블록이 더이상 아래로 못내려가는경우(아래쪽 겹치는 경우)
            if block.pos_y + block.list_offset_y[0] <= 0 : # 게임오버 조건
                running = False
            else:
                app_to_leaved_list(block.list_block_coordi)
                app_to_leaved_data(block.list_block_coordi, block.color)
                block.pos_x = 5
                block.pos_y = 0
                block.index = 0
                block.coordi_set() # 아래로 더이상 이동할수 없으면 좌표 초기화
                block.key_change() # 블록 키 바꾸기
                rand_next_block_key = rand_next_block_key = random.randint(0,6) # 다음블록키를 바꾸고 저장
                Next_block.key_change()
                Next_block.coordi_set()
                main_frame.mainField_blockremove()

            ################### NEXT 블럭 위치 가운데로 맞추기 위함 ##################### 
            block_x_size = 1
            block_y_size = 1

            for i in range(0,len(Next_block.list_offset_x)-1):
                if Next_block.list_offset_x[i] != Next_block.list_offset_x[i+1]:
                    block_x_size += 1
    
            for i in range(0,len(Next_block.list_offset_y)-1):
                if Next_block.list_offset_y[i] != Next_block.list_offset_y[i+1]:
                    block_y_size += 1

            if len(Next_block.offset_size) != 4:
                Next_block.pos_x = 13 + (4 - block_x_size)/2
                Next_block.pos_y = 9 + (4 -block_y_size)/2 
            else:
                Next_block.pos_x = 13
                Next_block.pos_y = 9
            
            Next_block.coordi_set()
            ############################################################################

    if sum_over != 3: # 겹침(111)X 아닐때 / 블록 회전시 좌,우,아래 3방향이 전부 겹치지 않는 경우
        if sum_over == 2: # (110)X ,(101)우이동 ,(011)좌이동
            if block_Overlaped[2] != 0: # (101)우 ,(011)좌
                if block_Overlaped[0] == 1: # (101)우
                    block.to_x += block.to_right
                else:
                # elif block_Overlaped[1] == 1: #(011)좌
                    block.to_x += block.to_left
        elif sum_over <= 1: #(100)우, (010)좌, (001) 좌우, (000) 좌우
            if block_Overlaped[0] == 0 and block_Overlaped[1] == 0: # (001) 좌우, (000) 좌우
                block.to_x = block.to_left + block.to_right
            else: # (100)우, (010)좌
                if block_Overlaped[0] == 1: # (100)우
                    block.to_x += block.to_right
                else: # (010)좌
                    block.to_x += block.to_left
        block.pos_x += block.to_x
    else:
        block.to_x = 0
        block.to_left = 0
        block.to_right = 0

    block.coordi_set() # 블록좌표 갱신
    
    list_mainField_coordi = main_frame.mainField_coordi() # 메인프레임 틀 좌표 담고있는 리스트변수
    sideBoard_frame_coordi = main_frame.sideBoard_coordi()
    blockBoard_frame_coordi = main_frame.blockBoard_coordi()
    
    
    # 5. 화면에 그리기
    main_frame.draw_lattice() # 격자 그리기
    draw_block(screen, block.color, block.list_block_coordi) # 현재 블록
    draw_block(screen, Next_block.color, Next_block.list_block_coordi) # NEXT 블록 그리기
    draw_block(screen, main_frame.frame_color, list_mainField_coordi) # 메인화면 프레임(틀)
    draw_block(screen, BLACK, sideBoard_frame_coordi)
    draw_block(screen, GRAY, blockBoard_frame_coordi)

    screen.blit(text_nextBlock,(360 + ((180 - text_nextBlock.get_rect().size[0]) / 2),\
         180 + ((60 - text_nextBlock.get_rect().size[1]) / 2)))
    screen.blit(text_game_score, (360 + ((180 - text_game_score.get_rect().size[0]) /2 ), \
        30 + ((120 - text_game_score.get_rect().size[1]) / 2)))


    for i in range(0, len(list_leaved_blocks_data)):
        draw_block(screen, list_leaved_blocks_data[i][-1], list_leaved_blocks_data[i][:-1]) # 남겨지는 블록


    pygame.display.update()

screen.blit(text_GameOver,(30 + ((300 - text_GameOver.get_rect().size[0]) /2 ), 260))
pygame.display.update()
pygame.time.delay(3000)
pygame.quit()