import data.Foo;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.Base64;
import lab.actions.common.serializable.AccessTokenUser;
import data.productcatalog.ProductTemplate;

class Main {
    public static void main(String[] args) throws Exception {

        // AccessTokenUser deserializedObject = deserialize("rO0ABXNyAC9sYWIuYWN0aW9ucy5jb21tb24uc2VyaWFsaXphYmxlLkFjY2Vzc1Rva2VuVXNlchlR/OUSJ6mBAgACTAALYWNjZXNzVG9rZW50ABJMamF2YS9sYW5nL1N0cmluZztMAAh1c2VybmFtZXEAfgABeHB0ACBnbTd2aWU4MHBxZjhnbmY3bGRtbmQ0dnk4cWJmZWlhdHQABndpZW5lcg==");

        // System.out.println(deserializedObject.getUsername());
        // System.out.println(deserializedObject.getAccessToken());

        // AccessTokenUser newObject = new AccessTokenUser("administrator", deserializedObject.getAccessToken());
        
        // String serializedObject = serialize(newObject);

        // System.out.println("Serialized object: " + serializedObject);

        ProductTemplate productTemplate = new ProductTemplate(args[0]);
        String serializedProductTemplate = serialize(productTemplate);
        System.out.println(serializedProductTemplate);

    }

    private static String serialize(Serializable obj) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream(512);
        try (ObjectOutputStream out = new ObjectOutputStream(baos)) {
            out.writeObject(obj);
        }
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }

    private static <T> T deserialize(String base64SerializedObj) throws Exception {
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(base64SerializedObj)))) {
            @SuppressWarnings("unchecked")
            T obj = (T) in.readObject();
            return obj;
        }
    }
}
