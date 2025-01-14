import os
import shutil
import json
import time
import sys

class Auto_backup:
    def __init__(self, source_path, backup_path, dataset_limit_counter, limit_file_size_gb):
        '''
        source_path: 백업을 수행해야 하는 경로
        backup_path: 백업 파일을 보관할 경로
        dataset_limit_counter: n개를 넘어가면 데이터셋이라 판단하고 그 경로는 백업에서 제외
        limit_file_size_gb: n GB를 넘어가는 파일을 백업에서 제외
        '''

        # 백업을 수행할 경로
        self.source_path = self.path_nor(source_path)
        self.backup_path = self.path_nor(backup_path)

        # 조건 상관 없이 무조건 백업하는 파일 포맷
        self.must_copy = {'pt', 'onnx', 'rknn', 'pst'} # 모델, 아웃룩

        # 데이터셋으로 인정할 확장자 입력
        dataset_formats = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'mp3', 'wav'}
        label_formats = {'json', 'txt'}
        self.dataset_formats = dataset_formats.union(label_formats)

        # 해당 폴더는 건너뛴다
        self.pass_dirs = {'.Trash-1000', '.vscode', 'lost+found', '__pycache__', '$RECYCLE.BIN'}
        
        # 데이터셋이 몇 개 이상이면 백업하지 않을 것인가
        self.dataset_limit_counter = dataset_limit_counter
        
        # 파일 하나의 용량이 몇 GB 이상이면 백업하지 않을 것인가
        self.limit_file_size_byte = limit_file_size_gb * 1024 * 1024 * 1024 # 바이트 > 키로바이트 > 메바가이트 > 기가바이트

        # 여기에 추가된 경로는 스캔을 멈춤(데이터셋이 존재할 경우)
        self.no_scan_path = set()

        # 복사 예외된 데이터 모음
        self.big_file_list = []
        self.is_file_big_error_list = []
        self.dataset_folder_list = []
        self.is_dataset_error_list = []
        self.auto_backup_error_list = []

        # 삭제 파일에 대체될 시그니처 파일명
        self.signiture_name = '[[자동백업제외]]'

    def is_dataset(self, path):
        '''
        해당 디렉토리가 데이터셋 폴더인지 판단하여 백업하지 않는다(너무 용량이 큼)
        - 디렉토리 안에 데이터셋으로 판단되는 파일들이 설정한 값 이상일 때 데이터셋 폴더로 판단
        - 데이터셋이 존재하는 폴더 안에 json파일을 넣고, 그 안에 원본 파일 리스트를 삽입함
        '''
        if path in self.no_scan_path:
            return True

        json_name = f'dataset_path{self.signiture_name}'
        try:
            # 제외 목록 만들기
            dataset_counter = 0
            file_list = []
            for file in os.listdir(path):
                if file.split('.')[-1] in self.dataset_formats:
                    dataset_counter += 1
                    file_list.append(file)
            if dataset_counter > self.dataset_limit_counter:
                self.no_scan_path.add(path)
                self.dataset_folder_list.append(path)
                # dataset의 정보가 담긴 json 생성
                self.make_json(os.path.join(self.sourcepath_to_backuppath(path), f'{json_name}.json'), file_list)
                return True
        except Exception as e:
            # 에러가 발생하면 복사를 하지 않는다
            print(f'is_dataset() error: {path}: {e}')
            self.is_dataset_error_list.append([path, e])
            return True
        return False

    def is_file_big(self, path):
        '''
        해당 파일의 용량이 백업 기준을 초과하는지 확인
        - 설정된 용량 이상의 파일은 백업하지 않음
        - 그 대신 json파일을 두고 파일의 원본 경로와 크기를 표시함
        '''
        json_name = f'gb_big_file{self.signiture_name}'
        try:
            size_byte = os.path.getsize(path)
            if size_byte > self.limit_file_size_byte: 
                self.big_file_list.append(path)
                byte_to_gb = round(size_byte/(1024*1024*1024), 2)
                # 정보 파일 json 저장
                data = {'경로':path, '용량(GB)':byte_to_gb}
                self.make_json(f'{self.sourcepath_to_backuppath(path)}_[{byte_to_gb}]{json_name}.json', data)
                return True
            else: 
                return False
        except Exception as e:
            # 에러가 발생하면 복사를 하지 않는다
            print(f'is_file_big() error: {path}: {e}')
            self.is_file_big_error_list.append([path, e])
            return True

    def save_log(self):
        '''
        필요 로그들을 백업이 완료된 이후 저장
        '''
        for data, file_name in zip([self.big_file_list, self.is_file_big_error_list, self.dataset_folder_list, self.is_dataset_error_list, self.auto_backup_error_list], 
                                   ['big_file_list', 'is_file_big_error_list', 'dataset_folder_list', 'is_dataset_error_list', 'auto_backup_error_list']):
            try:
                self.make_json(f'{self.backup_path}/log/{file_name}.json', data)
            except Exception as e:
                print(f'log save error:{file_name}')
                continue

    def path_nor(self, path):
        norm_path = os.path.normpath(path)
        norm_path = norm_path.replace('\\', '/')
        norm_path = norm_path.replace('//', '/')
        return norm_path

    def sourcepath_to_backuppath(self, root):
        '''
        source 경로를 backup 경로로 변경
        '''
        root = self.path_nor(root)
        tmp = root.replace(self.source_path, '') # 전체 경로에서 source_path를 제외함
        # tmp가 절대 경로로 오인되지 않도록 처리(join에서 문제 생김)
        if len(tmp) > 0:
            if tmp[0] == '/':
                tmp = tmp[1:]
        backup_path = os.path.join(self.backup_path, tmp)
        return backup_path

    def make_folders_and_count(self):
        '''
        - 전체 폴더 생성
        - tqdm을 위한 전체 개수 카운트
        '''
        start = time.time()
        print('folders making...')
        cnt = 0
        for root, _, _ in os.walk(self.source_path):
            # 백업 제외 폴더 확인
            if os.path.basename(root) in self.pass_dirs:
                continue
            to_dir = self.sourcepath_to_backuppath(root)
            self.makedirs_long(to_dir)
            cnt += 1
            if time.time() - start > 1:
                start = time.time()
                print(f'folders {cnt}ea created...')
        spent_time = int(time.time() - start)
        print(f'folders created: {cnt}ea! Auto backup system start...!')
        return cnt
        
    def make_json(self, path, data):
        '''
        data를 해당 경로에 저장
        - 디렉토리 자동 생성 기능
        - 한글 경로가 깨지지 않도록 ensure_ascii=False 적용
        '''
        self.makedirs_long(os.path.dirname(path)) # 폴더 자동 생성
        # json 작성
        with open(path, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def makedirs_long(self, path):
        # UNC 경로 적용
        unc_path = "\\\\?\\" + os.path.abspath(path)
        os.makedirs(unc_path, exist_ok=True)

    def auto_backup(self):
        '''
        자동 백업 수행
        '''
        total_cnt = self.make_folders_and_count()
        start = time.time()
        total_timer = time.time()
        for cnt, (root, dirs, files) in enumerate(os.walk(self.source_path)):
            root = self.path_nor(root)            
            # 백업 경로는 백업에서 제외
            if self.backup_path == root:
                continue
            
            # 백업 제외 폴더 확인
            if os.path.basename(root) in self.pass_dirs:
                continue
            
            # 현재 경로가 데이터셋 폴더인지
            if self.is_dataset(root) == True: continue
            
            # 파일 하나씩 백업
            for file in files:
                try:
                    # 파일이 너무 크면 건너뛰기
                    if self.is_file_big(f'{root}/{file}') == True and not file in self.must_copy:
                        continue
                    # 복사
                    to_dir = self.sourcepath_to_backuppath(root)
                    shutil.copy2(f'{root}/{file}', f'{to_dir}/{file}')
                except Exception as e:
                    print(f'auto_backup() error: {root}/{file}: {e}')
                    self.auto_backup_error_list.append([f'{root}/{file}', e])
            if time.time() - start > 3:
                print(f'completed: {cnt}/{total_cnt}')
                start = time.time()
        self.save_log()            
        print(f'Spend Time(sec): {int(time.time() - total_timer)}')
    

    