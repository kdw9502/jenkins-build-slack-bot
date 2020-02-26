import asyncio

from jenkinsapi.jenkins import Jenkins

from BaseBot import BaseBot


# noinspection NonAsciiCharacters
class JenkinsBuildBot(BaseBot):
    def __init__(self, bot_slack, user_slack, jenkins_url):
        self.favorites = []
        self.jenkins = Jenkins(jenkins_url, ssl_verify=False)
        BaseBot.__init__(self, bot_slack, user_slack)

    def _load_from_file(self):
        pass

    def _write_to_file(self):
        pass

    def 명령어(self):
        return "\n".join(["명령어 목록"] + list(self.help_dict.values()))

    def 작업목록(self):
        return self.작업검색()

    def 작업검색(self, 검색어=''):
        jobs = []
        for job_name in self.jenkins.get_jobs_list():
            if not 검색어 or 검색어.lower() in job_name.lower() and "OLD" not in job_name:
                jobs.append(job_name.replace(' ', '_'))

        return "\n".join(jobs)

    def 빌드상태(self, 작업이름):
        if not self.jenkins.has_job(작업이름):
            return "해당 작업이 존재하지 않습니다."

        job = self.jenkins.get_job(작업이름)

        if not job.is_queued_or_running():
            return "실행중인 빌드가 없습니다."

        response = self.jenkins.requester.get_and_confirm_status(
            f"{job.baseurl}/{job.get_last_buildnumber()}/wfapi/describe")

        json = response.json()
        return f"빌드 실행중입니다. 현재 {json['stages'][-1]['name']} 단계 빌드중입니다."

    async def 빌드시작(self, 작업이름):
        if not self.jenkins.has_job(작업이름):
            return "해당 작업이 존재하지 않습니다."

        job = self.jenkins.get_job(작업이름)

        if job.is_queued_or_running():
            return "이미 실행중인 빌드가 있습니다."

        build_parameter_dict = await self._start_conversation_and_return_parameter_dict(job)

        if build_parameter_dict is None:
            return "빌드시작을 취소했습니다."

        job.invoke(build_params=build_parameter_dict)

        build_num = job.get_last_buildnumber()

        return f"{작업이름} #{build_num}을 시작하였습니다."

    async def _start_conversation_and_return_parameter_dict(self, job):
        channel = self._last_message_channel
        user = self._last_message_user

        parameter_dict = dict()
        params = job.get_params()

        self._send_slack_message("빌드 파라미터를 입력해주세요.\n"
                                 "d 입력시 기본값, ad 입력시 입력하지 않은 값을 기본값으로 빌드합니다. "
                                 "cancel 또는 취소 입력시 빌드 시작을 취소합니다.")
        for param in params:
            param_name = param['name']
            default_value = param.get('defaultParameterValue', {}).get('value', '')
            self._send_slack_message(f"빌드 파라미터 {param_name} 의 값을 입력해주세요. "
                                     f"기본값: {default_value}")

            while True:
                input_parameter = await self._get_conversation_input(channel, user)

                input_parameter = input_parameter.strip().replace(' ', '').replace('\n', '').replace('\t', '')

                if self._validate_input_parameter(param, input_parameter):
                    break

                self._send_slack_message('잘못된 입력입니다. 다시 입력해주세요.')

            if input_parameter == 'ad':
                break
            elif input_parameter == 'd':
                pass
            elif input_parameter == '취소' or input_parameter == 'cancel':
                return None
            else:
                if input_parameter in ['False', 'True']:
                    input_parameter = input_parameter.lower()

                parameter_dict[param_name] = input_parameter

        return parameter_dict

    @staticmethod
    def _validate_input_parameter(param, input_parameter):
        is_bool_parameter = 'bool' in param['type'].lower()

        if is_bool_parameter and input_parameter not in ['true', 'True', 'false', 'False',
                                                         'ad', 'd', '취소', 'cancel']:
            return False

        return True

    async def _get_conversation_input(self, channel, user):
        while True:
            received_message = await self._receive_user_message()

            # FIXME: 지금은 대화메세지가 아니면 다시 일반 명령어로 처리해주지만, 구조적 개선이 필요하다.
            # FIXME: RTM 메세지 처리 클래스, 대화 클래스, 봇 클래스가 분리되는 편이 좋다.
            if self._last_message_user != user or self._last_message_channel != channel:
                await self._treat_received_message(message=received_message)

            else:
                break
            await asyncio.sleep(0.1)

        return received_message

    async def 빌드취소(self, 작업이름):
        if not self.jenkins.has_job(작업이름):
            return "해당 작업이 존재하지 않습니다."

        job = self.jenkins.get_job(작업이름)

        if not job.is_queued_or_running():
            return "실행중인 빌드가 없습니다."

        job.get_last_build().stop()

        build_num = job.get_last_buildnumber()

        return f"{작업이름} #{build_num}을 취소하였습니다."