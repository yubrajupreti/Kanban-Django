from rest_framework.test import APITestCase
from django.urls import reverse


class BoardTestSetUp(APITestCase):

    def setUp(self):
        breakpoint()
        self.board_url=reverse('board', kwargs={'version':'v1'})
        self.tag_url=reverse('tag')
        self.column_url=reverse('column')
        self.card_url=reverse('card')
        self.comment_url=reverse('comment')
        self.board_detail_url=reverse('board-list-detail')

        self.board_data={
            "name":"test_board",
            "owner":1,
            "members":[1,2,3]
        }




        return super().setUp()
    

    

    

    
    def tearDown(self) -> None:
        return super().tearDown()