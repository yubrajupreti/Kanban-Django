from .test_setup import BoardTestSetUp

class BoardTestView(BoardTestSetUp):

    def test_create_board_with_no_data(self):
        res=self.client.post(self.board_url)
        breakpoint()
        self.assertEqual(res.status_code,200)