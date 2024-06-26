-- Декларативная часть:
local host = '10.16.139.248'	   ----- Хост для подключения к базе данных
local port = '5432'				   ----- Порт для подключения к базе данных
local nodeSecurity = 'Server_IB'      ----- Имя узла с которого будут формироваться служебные события
local securityCategory = 5		   ----- Категория ИБ	

-- =============================================================================================================
local pgsql = require ('pgsql')    ----- Библиотека работы с PostgreSQl
local base64 = require('base64')

-- Задаваемые значения с видеокадра
local countEvents = Core['countEvents']	   			   ----- Количество событий, хранящихся в пределах одной базы данных		
local countWarningEvents = Core['countWarningEvents']  ----- Количество событий, при которых будут выдаваться предупредительные события
local dir  	----- Путь для сохранения выгрузки базы данных в CSV при переполнении
local nameFile = Core['nameFile'] 			   		   ----- Имя файла CSV	
local nameUser 	= Core['nameUser']			   		   ----- Имя пользователя от имени которого будут формироваться служебные события
local timePeriod = Core['timePeriod']	           	   ----- Период выдачи событий о переполнении таблицы БД в секундах (86400 - один раз в день )

local timestamp = 0				   ----- Переменная для фиксации времени отправки предупредительного события	
local conn						   ----- Переменная связи с базой данных
local value						   ----- Переменная для записи текущего объема таблицы в байтах 		
local db
local pr_conOk= false

-- Функция отправки сообщеия в журнал событий и в базу данных ИБ
local function setMsg(msg) Core.addEvent(msg, securityCategory,1,nodeSecurity,nameUser) end

------------наслучай, если не поставили слеш в пути --steam
local function addSlesh(d)
	if type(d)~= 'string' then return '' end
	if d:sub(-1) ~= '/' then  return d..'/'
	else return d
	end
end 

-------------------------------------------
local function getEdit(old,new)
	if old~=new then
		old = new
		return true , new
	else
		return false , old
	end
end
-------------------------------------------
local function saveSettings()	
	if Core['save'] then
		local eCountEvents,eCountWarningEvents,eDir,eNameFile,eTimePeriod
		eCountEvents,countEvents = getEdit(countEvents,Core['countEvents'])
		eCountWarningEvents,countWarningEvents = getEdit(countWarningEvents,Core['countWarningEvents'])
		eDir,dir = getEdit(dir,Core['dir'])
		eNameFile,nameFile = getEdit(nameFile,Core['nameFile'])
		eTimePeriod,timePeriod = getEdit(timePeriod,Core['timePeriod'])
		if eCountEvents or eCountWarningEvents or eDir or eNameFile or eTimePeriod then
			nameUser = Core['nameUser']	
			local config = string.format("Количество хранимых записей в таблице информационной безопасности:%s . Предупредительные события о переполнении базы данных при хранении: %s записей ",countEvents,countWarningEvents)
			local config_path = string.format("Место хранения выгруженной базы на диске %s . Шаблон имени файла %s . Период выдачи событий %s ,сек",dir,nameFile,timePeriod)		
			setMsg('Пользователь ИБ выполнивший изменения :'..nameUser)
			setMsg(config)
			setMsg(config_path)
		end
		Core.addLogMsg('Новые настройки БД "'..db..'" сохранены, пользователь '..nameUser,  "./IBsettinsgs.log") 
		Core['save'] = false
		dir= addSlesh(dir)
	end
end
---------------------------------
local function settingsCorrect()
	return countEvents ~= 0	and countWarningEvents ~= 0 and dir  ~= ''	and nameFile ~= '' and timePeriod ~= 0
end
-- Функция подключения к базе данных
local function getConnect(h,p,dbname,user,password)
	return pgsql.connectdb(string.format('host=%s port=%s dbname=%s user=%s password=%s', h, p, dbname, user, password))
end
-- Функция запроса размера таблицы БД
local function getSizeDB()
	return conn:execParams('SELECT count(*) FROM SecurityTable;')	
end


------------------------------------------------------------------------------------------------------------------------
--[[local function ChangePath() Core.dir = addSlesh(Core.dir) end  
Core.onExtChange({"dir"}, ChangePath)
]]
dir  = addSlesh(Core.dir)
--------------------------------------------------------------------------------------------------------------------------
while true do	
local connect = Core['connectBD']
db   = base64.decode(Core['nameBD'])
local user = base64.decode(Core['userBD'])
local password = base64.decode(Core['passBD'])
if Core.save then saveSettings() end
	if connect then
		if conn == nil then conn=getConnect(host, port, db, user, password)	end			
		if conn:status()  ~= pgsql.CONNECTION_OK  then
			conn=getConnect(host, port, db, user, password)
			Core['connectedBD'] = false			
		end
		if conn:status()  == pgsql.CONNECTION_OK then
			Core['connectedBD'] = true	
			saveSettings()
			if settingsCorrect() then			
				local res = getSizeDB()
				if res:status() == pgsql.PGRES_TUPLES_OK then value = res[1][1] 
				else 
					setMsg('База данных информационной безопасности пустая')
					Core.addLogMsg('База данных "'.. db..'" '..'пустая',  "./IBsettinsgs.log")
				end								
				if value ~= nil then
					local countCur = tonumber(value)
					local curtime = os.time()
					if (countCur > countWarningEvents) then
						local countLeft = math.floor(countEvents - countCur)
						if curtime > timestamp + timePeriod then
							setMsg('База данных информационной безопасности переполняется. Осталось записей: '..countLeft)
							timestamp = curtime
						end
					end
					if (countCur >= countEvents) or Core['DumpBD'] then
						local date = os.date('%Y%m%d_%H%M%S',curtime)
						local path = dir..nameFile..date..'.csv'
						Core.addLogMsg('Выполняю запись данных в csv файл  "'.. path,  "./IBsettinsgs.log")				
						local res = conn:exec(string.format("COPY securitytable TO \'%s\' WITH (FORMAT CSV, HEADER);",path))
						if res:status() == pgsql.PGRES_COMMAND_OK then 
							if Core['DumpBD'] then
								setMsg('База данных информационной безопасности была выгружена по запросу')
							else
								setMsg('База данных информационной безопасности была выгружена по переполнению')
							end
							res = conn:exec("DELETE FROM SecurityTable;")
							if res:status() == pgsql.PGRES_COMMAND_OK then 
								setMsg('База данных информационной безопасности была очищена '..date)
								Core.addLogMsg('База данных "'.. db..'" '..'очищена',  "./IBsettinsgs.log")
							end
						end
						
					end
				end
			end
		end
	else
		if conn ~= nil then
			Core['connectedBD'] = false
			conn = nil
		end
	end
 	Core['save'] = false
 	Core['DumpBD'] = false

	if conn~= nil and Core.connectedBD and not pr_conOk then Core.addLogMsg('Подключился к базе данных "'.. db..'"',  "./IBsettinsgs.log") end
	if not Core.connectedBD and pr_conOk then	
		local com = (conn~= nil) and conn:errorMessage() or ''
		Core.addLogMsg('Не могу подключиться к базе данных "'.. db..'"\n' .. com,  "./IBsettinsgs.log")
	end 
	pr_conOk = Core.connectedBD
	os.sleep(2)
end 

--Core.waitEvents()