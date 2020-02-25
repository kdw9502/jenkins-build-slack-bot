import asyncio

from BaseBot import BaseBot
from jenkinsapi.jenkins import Jenkins

# noinspection NonAsciiCharacters
class JenkinsBuildBot(BaseBot):
    def __init__(self, bot_slack, user_slack):
        self.favorites = []
        self.jenkins = Jenkins("http://10.0.47.146:8080/", ssl_verify=False)
        BaseBot.__init__(self, bot_slack, user_slack)

    def _load_from_file(self):
        pass

    def _write_to_file(self):
        pass

    def 명령어(self):
        return "\n".join(["명령어 목록"] + list(self.help_dict.values()))

    def 작업검색(self, 검색어):
        jobs = []
        for job_name in self.jenkins.get_jobs_list():
            if 검색어.lower() in job_name.lower() and "OLD" not in job_name:
                jobs.append(job_name.replace(' ','_'))

        return "\n".join(jobs)

    def 현재빌드목록(self):
        self.jenkins.get_queue()

    async def 빌드시작(self, 작업이름):
        if not self.jenkins.has_job(작업이름):
            return "해당 작업이 존재하지 않습니다."

        job = self.jenkins.get_job(작업이름)

        if job.is_queued_or_running():
            return "이미 실행중인 빌드가 있습니다."

        build_parameter_dict = dict()

        params = job.get_params()

        self._send_slack_message("빌드 파라미터를 입력해주세요.\n"
                                 "d 입력시 기본값, ad 입력시 입력하지 않은 값을 기본값으로 빌드합니다. "
                                 "cancel 또는 취소 입력시 빌드 시작을 취소합니다.")
        for param in params:
            param_name = param['name']
            default_value = param.get('defaultParameterValue',{}).get('value','')
            self._send_slack_message(f"빌드 파라미터 {param_name} 의 값을 입력해주세요. "
                                     f"기본값: {default_value}")

            await asyncio.sleep(0.1)
            input_param = await self._receive_slack_message()
            input_param = input_param.strip().replace(' ','').replace('\n','').replace('\t','')

            if input_param == 'ad':
                break
            elif input_param == 'd':
                pass
            elif input_param == '취소' or input_param == 'cancel':
                return "빌드시작을 취소했습니다."
            else:
                build_parameter_dict[param_name] = input_param

        job.invoke(build_params=build_parameter_dict)

        build_num = job.get_last_buildnumber()

        return f"{작업이름} #{build_num}을 작하였습니다."

    async def 빌드취소(self, 작업이름):
        if not self.jenkins.has_job(작업이름):
            return "해당 작업이 존재하지 않습니다."

        job = self.jenkins.get_job(작업이름)

        if not job.is_queued_or_running():
            return "실행중인 빌드가 없습니다."

        job.get_last_build().stop()

        build_num = job.get_last_buildnumber()

        return f"{작업이름} #{build_num}을 취소하였습니다."

    @staticmethod
    def _exception_handle_and_return_message(exception):
        return str(exception)
